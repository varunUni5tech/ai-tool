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
      const expr = p.expression || 'sin(x)';
      const minX = p.domain?.min ?? 0;
      const maxX = p.domain?.max ?? 6.28;
      const samples = p.domain?.samples ?? 200;

      const points: [number, number, number][] = [];
      for (let i = 0; i <= samples; i++) {
        const x = minX + (i / samples) * (maxX - minX);
        let y = Math.sin(x);
        if (expr.includes('cos')) y = Math.cos(x);
        if (expr.includes('exp')) y = Math.exp(-x / 2) * Math.cos(5 * x);
        points.push([x - (maxX - minX) / 2, y * 2, 0]);
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
