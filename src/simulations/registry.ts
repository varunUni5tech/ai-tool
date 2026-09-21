import { SimulationSpecInput, PrismSimulationResult } from './prism/types';
import { runPrismDispersionSimulation } from './prism/prismPhysics';

export type SimulationRunner = (spec: SimulationSpecInput) => any;

class SimulationRegistry {
  private registry = new Map<string, SimulationRunner>();

  constructor() {
    // 1. Prism Dispersion
    this.register('prism_dispersion', (spec: SimulationSpecInput): PrismSimulationResult => {
      return runPrismDispersionSimulation(spec.parameters as any);
    });

    // 2. Optical Prism Single-Ray Refraction
    this.register('optical_prism', (spec: SimulationSpecInput): PrismSimulationResult => {
      const params = spec.parameters as any;
      return runPrismDispersionSimulation({
        apex_angle: params.apex_angle || 60.0,
        incident_angle: params.incident_angle || 30.0,
        cauchy_b: params.refractive_index || 1.5,
        cauchy_c: 0.0, // single wavelength
        wavelengths_nm: [550.0], // Yellow 550nm
      });
    });

    // 3. Projectile Motion
    this.register('projectile_motion', (spec: SimulationSpecInput) => {
      const p = spec.parameters as any;
      const v0 = p.initial_velocity || 20.0;
      const angleDeg = p.launch_angle || 45.0;
      const g = p.gravity || 9.81;
      const rad = (angleDeg * Math.PI) / 180.0;
      const v0x = v0 * Math.cos(rad);
      const v0y = v0 * Math.sin(rad);
      const flightTime = (2 * v0y) / g;
      const maxH = (v0y * v0y) / (2 * g);
      const range = v0x * flightTime;

      const rays: any[] = [];
      const samples = 50;
      const points: [number, number, number][] = [];
      for (let i = 0; i <= samples; i++) {
        const t = (i / samples) * flightTime;
        const x = v0x * t;
        const y = Math.max(0, v0y * t - 0.5 * g * t * t);
        points.push([x - range / 2, y, 0]);
      }

      return {
        simulation_type: 'projectile_motion',
        domain: 'mechanics',
        prism: null,
        parameters: p,
        trajectoryPoints: points,
        summary: {
          flight_time_s: parseFloat(flightTime.toFixed(2)),
          max_height_m: parseFloat(maxH.toFixed(2)),
          horizontal_range_m: parseFloat(range.toFixed(2)),
        },
        rays: [
          {
            wavelengthNm: 550,
            refractiveIndex: 1.0,
            color: '#38bdf8',
            spectralName: 'Projectile Path',
            deviationAngleDeg: angleDeg,
            isTotalInternalReflection: false,
          },
        ],
      };
    });

    // 4. Math Function Plotting
    this.register('function_plot', (spec: SimulationSpecInput) => {
      const p = spec.parameters as any;
      const expr = (p.expression || 'sin(x)').toLowerCase().replace(/\s+/g, '');
      const minX = p.domain?.min ?? 0;
      const maxX = p.domain?.max ?? 6.28;
      const samples = p.domain?.samples ?? 200;

      const points: [number, number, number][] = [];
      for (let i = 0; i <= samples; i++) {
        const x = minX + (i / samples) * (maxX - minX);
        let y = 0;
        try {
          // Dynamic safe evaluation for sin(x), cos(x), sin(x)/cos(x), exp(-x), etc.
          const sin = Math.sin, cos = Math.cos, tan = Math.tan, exp = Math.exp, sqrt = Math.sqrt, log = Math.log, abs = Math.abs, pi = Math.PI;
          
          if (expr === 'sin(x)/cos(x)' || expr === 'tan(x)') {
            y = Math.tan(x);
          } else if (expr.includes('sin(x)/cos(x)')) {
            y = Math.sin(x) / (Math.cos(x) || 1e-6);
          } else {
            // Replace x with current value and evaluate safely
            const sanitizedExpr = expr
              .replace(/sin/g, 'Math.sin')
              .replace(/cos/g, 'Math.cos')
              .replace(/tan/g, 'Math.tan')
              .replace(/exp/g, 'Math.exp')
              .replace(/sqrt/g, 'Math.sqrt')
              .replace(/abs/g, 'Math.abs')
              .replace(/\bx\b/g, `(${x})`);
            y = Function(`"use strict"; return (${sanitizedExpr})`)();
          }
        } catch (e) {
          y = Math.sin(x);
        }

        // Clamp y values for vertical asymptotes like tan(x) to prevent graph exploding offscreen
        const clampedY = Math.max(-10, Math.min(10, Number.isFinite(y) ? y : 0));
        points.push([x - (maxX - minX) / 2, clampedY, 0]);
      }

      return {
        simulation_type: 'function_plot',
        domain: 'mathematics',
        prism: null,
        parameters: p,
        trajectoryPoints: points,
        summary: {
          expression: expr,
          domain_min: minX,
          domain_max: maxX,
          samples,
        },
        rays: [
          {
            wavelengthNm: 500,
            refractiveIndex: 1.0,
            color: '#a855f7',
            spectralName: `y = ${expr}`,
            deviationAngleDeg: 0,
            isTotalInternalReflection: false,
          },
        ],
      };
    });
  }

  public register(type: string, runner: SimulationRunner): void {
    this.registry.set(type.toLowerCase(), runner);
  }

  public run(spec: SimulationSpecInput): any {
    const runner = this.registry.get(spec.simulation_type.toLowerCase());
    if (!runner) {
      // Default fallback
      return runPrismDispersionSimulation(spec.parameters as any);
    }
    return runner(spec);
  }

  public getSupportedTypes(): string[] {
    return Array.from(this.registry.keys());
  }
}

export const simulationRegistry = new SimulationRegistry();
