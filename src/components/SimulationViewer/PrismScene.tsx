import React, { useMemo, useRef, useEffect } from 'react';
import * as THREE from 'three';
import { OrbitControls, Html, Grid, Line } from '@react-three/drei';
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib';
import { PrismSimulationResult } from '../../simulations/prism/types';
import { DisplayOptions } from '../Controls/SimulationControls';

interface PrismSceneProps {
  result: PrismSimulationResult | any;
  displayOptions: DisplayOptions;
  animProgress: number; // 0.0 to 1.0 animation progress
  cameraView: 'default' | 'top' | 'front' | 'side';
}

export const PrismScene: React.FC<PrismSceneProps> = ({
  result,
  displayOptions,
  animProgress,
  cameraView,
}) => {
  const controlsRef = useRef<OrbitControlsImpl>(null);

  // Handle camera preset view shifts
  useEffect(() => {
    if (!controlsRef.current) return;
    const controls = controlsRef.current;
    if (cameraView === 'default') {
      controls.object.position.set(6, 4, 7);
      controls.target.set(0, 0, 0);
    } else if (cameraView === 'top') {
      controls.object.position.set(0, 10, 0.001);
      controls.target.set(0, 0, 0);
    } else if (cameraView === 'front') {
      controls.object.position.set(0, 0, 10);
      controls.target.set(0, 0, 0);
    } else if (cameraView === 'side') {
      controls.object.position.set(10, 0, 0);
      controls.target.set(0, 0, 0);
    }
    controls.update();
  }, [cameraView]);

  if (!result) return null;

  const { prism, rays, trajectoryPoints, simulation_type } = result;

  // Build extruded 3D triangular prism geometry from 2D vertices if prism simulation
  const prismGeometry = useMemo(() => {
    if (!prism || !prism.vertices2D) return null;
    const shape = new THREE.Shape();
    const [v0, v1, v2] = prism.vertices2D;
    shape.moveTo(v0[0], v0[1]);
    shape.lineTo(v1[0], v1[1]);
    shape.lineTo(v2[0], v2[1]);
    shape.closePath();

    const extrudeSettings = {
      depth: prism.extrusionDepth,
      bevelEnabled: true,
      bevelSegments: 2,
      steps: 1,
      bevelSize: 0.05,
      bevelThickness: 0.05,
    };

    const geom = new THREE.ExtrudeGeometry(shape, extrudeSettings);
    geom.center(); // Center at origin
    return geom;
  }, [prism]);

  // First ray incident path for white beam
  const incidentRay = rays && rays[0]?.incident;

  // Slice animated trajectory points for projectile/function simulations
  const visibleTrajectoryPoints = useMemo(() => {
    if (!trajectoryPoints || trajectoryPoints.length < 2) return [];
    const count = Math.max(2, Math.floor(trajectoryPoints.length * animProgress));
    return trajectoryPoints.slice(0, count);
  }, [trajectoryPoints, animProgress]);

  const projectileHead = visibleTrajectoryPoints.length > 0 ? visibleTrajectoryPoints[visibleTrajectoryPoints.length - 1] : null;

  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.6} />
      <directionalLight position={[10, 15, 10]} intensity={1.2} castShadow />
      <directionalLight position={[-10, -10, -5]} intensity={0.4} />
      <pointLight position={[0, 5, 0]} intensity={0.8} color="#e6f2ff" />

      {/* Camera Controls */}
      <OrbitControls
        ref={controlsRef}
        makeDefault
        enableDamping
        dampingFactor={0.05}
        minDistance={2}
        maxDistance={25}
      />

      {/* Grid Plane */}
      {displayOptions.showGrid && (
        <Grid
          position={[0, -2.5, 0]}
          args={[20, 20]}
          cellSize={1}
          cellThickness={1}
          cellColor="#334155"
          sectionSize={5}
          sectionThickness={1.5}
          sectionColor="#0284c7"
          fadeDistance={25}
        />
      )}

      {/* XYZ Coordinate Axes */}
      {displayOptions.showAxes && <axesHelper args={[4]} position={[0, 0.01, 0]} />}

      {/* Render 3D Trajectory Curve for Projectile & Function Plot */}
      {trajectoryPoints && visibleTrajectoryPoints.length >= 2 && (
        <group key={`trajectory-${simulation_type}-${animProgress}`}>
          <Line
            points={visibleTrajectoryPoints}
            color={simulation_type === 'projectile_motion' ? '#e377c2' : '#a855f7'}
            lineWidth={5}
          />

          {/* Projectile Sphere */}
          {projectileHead && (
            <mesh position={projectileHead}>
              <sphereGeometry args={[0.3, 16, 16]} />
              <meshStandardMaterial
                color={simulation_type === 'projectile_motion' ? '#ff79c6' : '#c084fc'}
                emissive={simulation_type === 'projectile_motion' ? '#ff79c6' : '#c084fc'}
                emissiveIntensity={0.6}
              />
            </mesh>
          )}

          {/* 3D Label */}
          {displayOptions.showLabels && projectileHead && (
            <Html position={[projectileHead[0], projectileHead[1] + 0.5, projectileHead[2]]}>
              <div className="flex items-center space-x-1.5 px-2 py-1 bg-slate-950/90 text-[10px] font-mono rounded border border-slate-700 shadow-xl backdrop-blur-md whitespace-nowrap">
                <span className="font-bold text-pink-400">
                  {simulation_type === 'projectile_motion' ? 'Projectile Pos' : 'Function y(x)'}
                </span>
                <span className="text-cyan-300">
                  ({projectileHead[0].toFixed(1)}, {projectileHead[1].toFixed(1)})
                </span>
              </div>
            </Html>
          )}
        </group>
      )}

      {/* 3D Glass Triangular Prism Mesh */}
      {prism && prismGeometry && (
        <mesh key={`prism-${prism.apexAngleDeg}`} geometry={prismGeometry} position={[0, 0, 0]}>
          <meshPhysicalMaterial
            transparent
            opacity={0.5}
            transmission={0.9}
            ior={1.5}
            roughness={0.1}
            metalness={0.0}
            color="#d0e8ff"
            reflectivity={0.9}
            clearcoat={1.0}
          />
        </mesh>
      )}

      {/* Incident White Light Beam */}
      {displayOptions.showIncidentRay && incidentRay && (
        <group key={`incident-group-${incidentRay.intersection.x}-${incidentRay.intersection.y}`}>
          {[-0.4, 0.0, 0.4].map((zOffset, idx) => {
            const p0 = incidentRay.origin.clone();
            p0.z += zOffset;
            const p1 = incidentRay.intersection.clone();
            p1.z += zOffset;

            // Interpolate ray based on animProgress
            const currentP1 = p0.clone().lerp(p1, Math.min(1.0, animProgress * 3.0));

            return (
              <Line
                key={`incident-line-${idx}-${p0.x}-${p0.y}-${currentP1.x}`}
                points={[
                  [p0.x, p0.y, p0.z],
                  [currentP1.x, currentP1.y, currentP1.z],
                ]}
                color="#FFFFFF"
                lineWidth={4}
              />
            );
          })}
        </group>
      )}

      {/* Refracted Internal & Emergent Outgoing Spectral Rays */}
      {prism && rays && rays.map((ray: any) => {
        if (!ray.inside || !ray.outgoing) return null;
        const p1 = ray.inside.origin.clone();
        const p2 = ray.inside.intersection.clone();
        const p3 = ray.outgoing.endPoint.clone();

        const p2Animated = p1.clone().lerp(p2, Math.min(1.0, Math.max(0.0, (animProgress - 0.33) * 3.0)));
        const p3Animated = p2.clone().lerp(p3, Math.min(1.0, Math.max(0.0, (animProgress - 0.66) * 3.0)));

        return (
          <group key={`ray-group-${ray.wavelengthNm}-${p1.x}-${p2.x}-${p3.x}`}>
            {[-0.4, 0.0, 0.4].map((zOffset, zIdx) => {
              const p1Z = p1.clone(); p1Z.z += zOffset;
              const p2ZAnimated = p2Animated.clone(); p2ZAnimated.z += zOffset;
              const p2Z = p2.clone(); p2Z.z += zOffset;
              const p3ZAnimated = p3Animated.clone(); p3ZAnimated.z += zOffset;

              return (
                <group key={`ray-z-${zIdx}`}>
                  {/* Internal Ray inside Prism */}
                  {displayOptions.showInternalRays && animProgress > 0.33 && (
                    <Line
                      key={`internal-line-${ray.wavelengthNm}-${zIdx}-${p1Z.x}-${p2ZAnimated.x}`}
                      points={[
                        [p1Z.x, p1Z.y, p1Z.z],
                        [p2ZAnimated.x, p2ZAnimated.y, p2ZAnimated.z],
                      ]}
                      color={ray.color}
                      linewidth={3}
                    />
                  )}

                  {/* Outgoing Emergent Spectral Ray */}
                  {displayOptions.showSpectrum && animProgress > 0.66 && (
                    <Line
                      key={`outgoing-line-${ray.wavelengthNm}-${zIdx}-${p2Z.x}-${p3ZAnimated.x}`}
                      points={[
                        [p2Z.x, p2Z.y, p2Z.z],
                        [p3ZAnimated.x, p3ZAnimated.y, p3ZAnimated.z],
                      ]}
                      color={ray.color}
                      lineWidth={4}
                    />
                  )}
                </group>
              );
            })}

            {/* 3D Wavelength & Refractive Index HTML Label */}
            {displayOptions.showLabels && animProgress > 0.66 && (
              <Html position={[p3.x + 0.3, p3.y + (ray.wavelengthNm - 550) * 0.003, p3.z]} distanceFactor={10}>
                <div className="flex items-center space-x-1.5 px-2 py-1 bg-slate-950/90 text-[10px] font-mono rounded border border-slate-700 shadow-xl backdrop-blur-md whitespace-nowrap select-none">
                  <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: ray.color }} />
                  <span className="font-bold text-white">{ray.wavelengthNm} nm</span>
                  <span className="text-amber-400">n={ray.refractiveIndex.toFixed(4)}</span>
                  <span className="text-emerald-400">δ={ray.deviationAngleDeg.toFixed(1)}°</span>
                </div>
              </Html>
            )}
          </group>
        );
      })}
    </>
  );
};
