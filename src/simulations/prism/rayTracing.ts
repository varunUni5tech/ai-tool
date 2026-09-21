import * as THREE from 'three';
import { degToRad, radToDeg } from '../../utils/units';
import { refractVector3D, rayPlaneIntersection } from '../../utils/vectorMath';
import { wavelengthToHexColor, getSpectralName } from '../../utils/wavelengthColor';
import { PrismGeometryInfo, RayPath3D } from './types';

/**
 * Calculates 3D ray trace for a specific wavelength through a triangular prism using Snell's Law.
 */
export function traceRay3D(
  wavelengthNm: number,
  refractiveIndex: number,
  incidentAngleDeg: number,
  prism: PrismGeometryInfo
): RayPath3D {
  const i1Rad = degToRad(incidentAngleDeg);

  // Surface 1 (Left face) midpoint
  const p1 = new THREE.Vector3(-prism.baseWidth / 4.0, 0.0, 0.0);

  // Face 1 Normal pointing outwards
  const N1 = prism.face1Normal.clone();

  // Face 1 tangential vector pointing along face (towards apex)
  const face1Dir = new THREE.Vector3(
    prism.vertices2D[1][0] - prism.vertices2D[0][0],
    prism.vertices2D[1][1] - prism.vertices2D[0][1],
    0
  ).normalize();

  // Construct Incident Ray Direction pointing TOWARDS p1 at angle i1 relative to N1
  // Rotate (-N1) by i1 degrees towards base (-face1Dir)
  const incDir = N1.clone().negate().applyAxisAngle(new THREE.Vector3(0, 0, 1), i1Rad).normalize();

  // Origin of Incident Ray (3.5 units back along -incDir)
  const p0 = p1.clone().sub(incDir.clone().multiplyScalar(3.5));

  // 1. First Refraction at Surface 1 (Air n=1.0 -> Prism n=refractiveIndex)
  const insideDir = refractVector3D(incDir, N1, 1.0, refractiveIndex);
  
  if (!insideDir) {
    // Should not happen at entry surface
    const fallbackDir = incDir.clone();
    return {
      wavelengthNm,
      refractiveIndex,
      color: wavelengthToHexColor(wavelengthNm),
      spectralName: getSpectralName(wavelengthNm),
      incident: { origin: p0, direction: incDir, intersection: p1 },
      inside: { origin: p1, direction: fallbackDir, intersection: p1.clone().add(fallbackDir) },
      outgoing: { origin: p1.clone().add(fallbackDir), direction: fallbackDir, endPoint: p1.clone().add(fallbackDir.multiplyScalar(3)) },
      deviationAngleDeg: 0,
      isTotalInternalReflection: true,
    };
  }

  // 2. Traversal through Prism to Surface 2 (Right face plane)
  const face2Midpoint = new THREE.Vector3(prism.baseWidth / 4.0, 0.0, 0.0);
  const N2 = prism.face2Normal.clone(); // Face 2 normal pointing outwards

  const p2 = rayPlaneIntersection(p1, insideDir, face2Midpoint, N2) || new THREE.Vector3(prism.baseWidth / 4.0, 0.0, 0.0);

  // 3. Second Refraction at Surface 2 (Prism n=refractiveIndex -> Air n=1.0)
  // Inside ray hits surface 2 from inside, so surface normal inside is N2
  const outgoingDir = refractVector3D(insideDir, N2.clone().negate(), refractiveIndex, 1.0);

  const isTIR = outgoingDir === null;
  const finalOutgoingDir = outgoingDir ? outgoingDir : insideDir.clone().reflect(N2).normalize();

  // End point for outgoing ray visualization
  const p3 = p2.clone().add(finalOutgoingDir.clone().multiplyScalar(4.0));

  // Deviation Angle delta = angle between incident direction and outgoing direction
  let deviationAngleDeg = 0.0;
  if (!isTIR) {
    const dot = Math.min(1.0, Math.max(-1.0, incDir.dot(finalOutgoingDir)));
    deviationAngleDeg = radToDeg(Math.acos(dot));
  }

  return {
    wavelengthNm,
    refractiveIndex: parseFloat(refractiveIndex.toFixed(5)),
    color: wavelengthToHexColor(wavelengthNm),
    spectralName: getSpectralName(wavelengthNm),
    incident: {
      origin: p0,
      direction: incDir,
      intersection: p1,
    },
    inside: {
      origin: p1,
      direction: insideDir,
      intersection: p2,
    },
    outgoing: {
      origin: p2,
      direction: finalOutgoingDir,
      endPoint: p3,
    },
    deviationAngleDeg: parseFloat(deviationAngleDeg.toFixed(4)),
    isTotalInternalReflection: isTIR,
  };
}
