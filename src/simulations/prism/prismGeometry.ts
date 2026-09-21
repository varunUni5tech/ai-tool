import * as THREE from 'three';
import { degToRad } from '../../utils/units';
import { PrismGeometryInfo } from './types';

/**
 * Calculates 3D triangular prism mesh geometry dynamically from parameters.apex_angle.
 */
export function buildPrismGeometryInfo(
  apexAngleDeg: number,
  sideLength: number = 4.0,
  extrusionDepth: number = 4.0
): PrismGeometryInfo {
  const A = degToRad(apexAngleDeg);
  const halfA = A / 2.0;

  const height = sideLength * Math.cos(halfA);
  const baseWidth = 2.0 * sideLength * Math.sin(halfA);

  const leftV: [number, number] = [-baseWidth / 2.0, -height / 2.0];
  const apexV: [number, number] = [0.0, height / 2.0];
  const rightV: [number, number] = [baseWidth / 2.0, -height / 2.0];

  const zHalf = extrusionDepth / 2.0;

  const vertices3D: THREE.Vector3[] = [
    new THREE.Vector3(leftV[0], leftV[1], -zHalf),
    new THREE.Vector3(apexV[0], apexV[1], -zHalf),
    new THREE.Vector3(rightV[0], rightV[1], -zHalf),
    new THREE.Vector3(leftV[0], leftV[1], zHalf),
    new THREE.Vector3(apexV[0], apexV[1], zHalf),
    new THREE.Vector3(rightV[0], rightV[1], zHalf),
  ];

  // Face 1 (Left face: from LeftV to ApexV)
  // Vector along face: ApexV - LeftV = (baseWidth/2, height)
  // Normal pointing outwards (to the left/up): (-height, baseWidth/2)
  const face1Dir = new THREE.Vector2(apexV[0] - leftV[0], apexV[1] - leftV[1]).normalize();
  const face1Normal2D = new THREE.Vector2(-face1Dir.y, face1Dir.x).normalize();
  const face1Normal = new THREE.Vector3(face1Normal2D.x, face1Normal2D.y, 0).normalize();

  // Face 2 (Right face: from ApexV to RightV)
  // Vector along face: RightV - ApexV = (baseWidth/2, -height)
  // Normal pointing outwards (to the right/up): (height, baseWidth/2)
  const face2Dir = new THREE.Vector2(rightV[0] - apexV[0], rightV[1] - apexV[1]).normalize();
  const face2Normal2D = new THREE.Vector2(-face2Dir.y, face2Dir.x).normalize();
  const face2Normal = new THREE.Vector3(face2Normal2D.x, face2Normal2D.y, 0).normalize();

  return {
    apexAngleDeg,
    height,
    baseWidth,
    extrusionDepth,
    vertices2D: [leftV, apexV, rightV],
    vertices3D,
    face1Normal,
    face2Normal,
  };
}
