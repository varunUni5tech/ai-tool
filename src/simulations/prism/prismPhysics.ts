import { PrismParameters, PrismSimulationResult, RayPath3D } from './types';
import { buildPrismGeometryInfo } from './prismGeometry';
import { calculateCauchyRefractiveIndex } from './dispersion';
import { traceRay3D } from './rayTracing';

/**
 * Runs deterministic Prism Dispersion physics calculation from input parameters.
 */
export function runPrismDispersionSimulation(params: PrismParameters): PrismSimulationResult {
  const prism = buildPrismGeometryInfo(params.apex_angle);

  const rays: RayPath3D[] = [];
  const deviations: number[] = [];

  // Sort wavelengths reverse (Red 700nm to Violet 420nm)
  const wavelengths = [...params.wavelengths_nm].sort((a, b) => b - a);

  for (const wl of wavelengths) {
    const n = calculateCauchyRefractiveIndex(wl, params.cauchy_b, params.cauchy_c);
    const rayPath = traceRay3D(wl, n, params.incident_angle, prism);
    rays.push(rayPath);
    if (!rayPath.isTotalInternalReflection) {
      deviations.push(rayPath.deviationAngleDeg);
    }
  }

  const minDev = deviations.length > 0 ? Math.min(...deviations) : 0;
  const maxDev = deviations.length > 0 ? Math.max(...deviations) : 0;
  const angularDispersion = parseFloat((maxDev - minDev).toFixed(4));

  return {
    simulation_type: 'prism_dispersion',
    domain: 'optics',
    prism,
    parameters: params,
    rays,
    minDeviationDeg: parseFloat(minDev.toFixed(4)),
    maxDeviationDeg: parseFloat(maxDev.toFixed(4)),
    angularDispersionDeg: angularDispersion,
  };
}
