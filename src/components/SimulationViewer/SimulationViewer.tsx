import React, { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { PrismScene } from './PrismScene';
import { PrismSimulationResult } from '../../simulations/prism/types';
import { DisplayOptions } from '../Controls/SimulationControls';
import { Box, Maximize2, RefreshCw } from 'lucide-react';

interface SimulationViewerProps {
  result: PrismSimulationResult | null;
  displayOptions: DisplayOptions;
  isPlaying: boolean;
  speed: number;
  resetTrigger: number;
  cameraView: 'default' | 'top' | 'front' | 'side';
}

export const SimulationViewer: React.FC<SimulationViewerProps> = ({
  result,
  displayOptions,
  isPlaying,
  speed,
  resetTrigger,
  cameraView,
}) => {
  const [animProgress, setAnimProgress] = useState<number>(1.0);

  // Animation Loop handling
  useEffect(() => {
    setAnimProgress(0.0);
  }, [resetTrigger, result]);

  useEffect(() => {
    if (!isPlaying) return;

    let animId: number;
    let lastTime = performance.now();

    const animate = (now: number) => {
      const dt = (now - lastTime) / 1000.0;
      lastTime = now;

      setAnimProgress((prev) => {
        const next = prev + dt * 0.5 * speed;
        if (next >= 1.0) {
          return next % 1.0;
        }
        return next;
      });

      animId = requestAnimationFrame(animate);
    };

    animId = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(animId);
  }, [isPlaying, speed]);

  return (
    <div className="relative w-full h-full min-h-[400px] bg-white border border-slate-200 rounded-xl overflow-hidden shadow-md flex flex-col">
      {/* Viewport Top Header Bar */}
      <div className="absolute top-3 left-3 z-10 flex items-center space-x-2 bg-white/90 px-3 py-1.5 rounded-lg border border-slate-200 backdrop-blur-md shadow-sm">
        <Box className="w-4 h-4 text-blue-600 animate-pulse" />
        <span className="text-xs font-mono font-bold text-slate-800">
          3D WebGL Viewport • Three.js
        </span>
      </div>

      {/* R3F Canvas */}
      <div className="flex-1 w-full h-full relative cursor-grab active:cursor-grabbing">
        <Canvas
          camera={{ position: [6, 4, 7], fov: 45 }}
          gl={{ antialias: true, alpha: false }}
          shadows
        >
          <color attach="background" args={['#0f172a']} />
          <PrismScene
            result={result}
            displayOptions={displayOptions}
            animProgress={animProgress}
            cameraView={cameraView}
          />
        </Canvas>
      </div>
    </div>
  );
};
