import * as THREE from 'three';

/**
 * Calculates Snell's Law refraction vector in 3D space.
 * @param incident Incident unit vector pointing TOWARDS the surface intersection.
 * @param normal Unit normal vector of surface pointing OUTWARDS (opposite to incident).
 * @param n1 Refractive index of medium 1.
 * @param n2 Refractive index of medium 2.
 * @returns Refracted unit vector or null if Total Internal Reflection (TIR) occurs.
 */
export function refractVector3D(
  incident: THREE.Vector3,
  normal: THREE.Vector3,
  n1: number,
  n2: number
): THREE.Vector3 | null {
  const I = incident.clone().normalize();
  let N = normal.clone().normalize();
  
  let eta = n1 / n2;
  let cosI = -N.dot(I);

  // If ray is coming from inside medium, flip normal
  if (cosI < 0) {
    cosI = -cosI;
    N.negate();
  }

  const k = 1.0 - eta * eta * (1.0 - cosI * cosI);
  if (k < 0.0) {
    // Total Internal Reflection
    return null;
  }

  // Refracted ray direction vector: eta*I + (eta*cosI - sqrt(k))*N
  const R = I.multiplyScalar(eta).add(N.multiplyScalar(eta * cosI - Math.sqrt(k))).normalize();
  return R;
}

/**
 * Finds intersection point of a ray with a plane defined by a point and normal.
 */
export function rayPlaneIntersection(
  rayOrigin: THREE.Vector3,
  rayDir: THREE.Vector3,
  planePoint: THREE.Vector3,
  planeNormal: THREE.Vector3
): THREE.Vector3 | null {
  const denom = planeNormal.dot(rayDir);
  if (Math.abs(denom) < 1e-6) {
    return null; // Parallel
  }
  const t = planePoint.clone().sub(rayOrigin).dot(planeNormal) / denom;
  if (t < 0) {
    return null; // Behind origin
  }
  return rayOrigin.clone().add(rayDir.clone().multiplyScalar(t));
}
