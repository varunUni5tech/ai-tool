import * as THREE from 'three';

export interface PrismParameters {
  apex_angle: number;
  incident_angle: number;
  cauchy_b: number;
  cauchy_c: number;
  wavelengths_nm: number[];
}

export interface SimulationSpecInput {
  simulation_schema_version: string;
  simulation_type: string;
  domain: string;
  parameters: PrismParameters;
  visualization?: Record<string, any>;
  educational?: Record<string, any>;
}

export interface RayPath3D {
  wavelengthNm: number;
  refractiveIndex: number;
  color: string;
  spectralName: string;
  incident: {
    origin: THREE.Vector3;
    direction: THREE.Vector3;
    intersection: THREE.Vector3;
  };
  inside: {
    origin: THREE.Vector3;
    direction: THREE.Vector3;
    intersection: THREE.Vector3;
  };
  outgoing: {
    origin: THREE.Vector3;
    direction: THREE.Vector3;
    endPoint: THREE.Vector3;
  };
  deviationAngleDeg: number;
  isTotalInternalReflection: boolean;
}

export interface PrismGeometryInfo {
  apexAngleDeg: number;
  height: number;
  baseWidth: number;
  extrusionDepth: number;
  vertices2D: [number, number][]; // Left, Apex, Right
  vertices3D: THREE.Vector3[];
  face1Normal: THREE.Vector3;
  face2Normal: THREE.Vector3;
}

export interface PrismSimulationResult {
  simulation_type: string;
  domain: string;
  prism: PrismGeometryInfo;
  parameters: PrismParameters;
  rays: RayPath3D[];
  minDeviationDeg: number;
  maxDeviationDeg: number;
  angularDispersionDeg: number;
}
