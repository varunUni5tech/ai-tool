import { nmToMicrometers } from '../../utils/units';

/**
 * Calculates wavelength-dependent refractive index n(lambda) via Cauchy equation:
 * n(lambda) = B + C / (lambda_um ^ 2)
 */
export function calculateCauchyRefractiveIndex(
  wavelengthNm: number,
  cauchyB: number,
  cauchyC: number
): number {
  const lambdaUm = nmToMicrometers(wavelengthNm);
  if (lambdaUm <= 0) return cauchyB;
  return cauchyB + cauchyC / (lambdaUm * lambdaUm);
}
