import React from 'react';
import { Play, Pause, RotateCcw, Eye, Grid as GridIcon, Compass, Tag, Layers, Sliders } from 'lucide-react';

export interface DisplayOptions {
  showGrid: boolean;
  showAxes: boolean;
  showLabels: boolean;
  showIncidentRay: boolean;
  showInternalRays: boolean;
  showSpectrum: boolean;
  showMeasurements: boolean;
}

interface SimulationControlsProps {
  isPlaying: boolean;
  onPlayPause: () => void;
  onResetAnimation: () => void;
  speed: number;
  onSpeedChange: (speed: number) => void;
  displayOptions: DisplayOptions;
  onToggleDisplayOption: (key: keyof DisplayOptions) => void;
  onSetCameraView: (view: 'default' | 'top' | 'front' | 'side') => void;
}

export const SimulationControls: React.FC<SimulationControlsProps> = ({
  isPlaying,
  onPlayPause,
  onResetAnimation,
  speed,
  onSpeedChange,
  displayOptions,
  onToggleDisplayOption,
  onSetCameraView,
}) => {
  return (
    <div className="flex flex-col space-y-3 bg-slate-900/90 border border-slate-800 p-4 rounded-xl shadow-xl backdrop-blur-md">
      {/* Animation Playback Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <button
            onClick={onPlayPause}
            className={`flex items-center space-x-2 px-4 py-1.5 rounded-lg font-semibold text-xs transition-all shadow-md active:scale-95 ${
              isPlaying
                ? 'bg-amber-500 hover:bg-amber-400 text-slate-950'
                : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950'
            }`}
          >
            {isPlaying ? (
              <>
                <Pause className="w-4 h-4 fill-current" />
                <span>Pause</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Play Simulation</span>
              </>
            )}
          </button>
          <button
            onClick={onResetAnimation}
            className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 rounded-lg transition-all"
            title="Reset Ray Propagation Animation"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
        </div>

        {/* Speed Slider */}
        <div className="flex items-center space-x-2 bg-slate-950/60 px-3 py-1.5 rounded-lg border border-slate-800">
          <Sliders className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-xs font-mono text-slate-400">Speed:</span>
          <input
            type="range"
            min="0.2"
            max="3.0"
            step="0.1"
            value={speed}
            onChange={(e) => onSpeedChange(parseFloat(e.target.value))}
            className="w-20 accent-cyan-400 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
          />
          <span className="text-xs font-mono font-semibold text-cyan-400 w-8 text-right">
            {speed.toFixed(1)}x
          </span>
        </div>
      </div>

      {/* Camera Views & Display Toggles */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
        {/* Camera Preset Buttons */}
        <div className="flex items-center space-x-1">
          <span className="text-slate-400 font-mono text-[11px] mr-1">Camera:</span>
          <button
            onClick={() => onSetCameraView('default')}
            className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[11px] transition-all"
          >
            Reset Camera
          </button>
          <button
            onClick={() => onSetCameraView('top')}
            className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[11px] transition-all"
          >
            Top View
          </button>
          <button
            onClick={() => onSetCameraView('front')}
            className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[11px] transition-all"
          >
            Front View
          </button>
          <button
            onClick={() => onSetCameraView('side')}
            className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[11px] transition-all"
          >
            Side View
          </button>
        </div>

        {/* Visibility Toggles */}
        <div className="flex flex-wrap items-center gap-1.5">
          <button
            onClick={() => onToggleDisplayOption('showGrid')}
            className={`flex items-center space-x-1 px-2 py-1 rounded text-[11px] font-medium transition-all ${
              displayOptions.showGrid
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-700/50'
                : 'bg-slate-800/60 text-slate-400 hover:bg-slate-800'
            }`}
          >
            <GridIcon className="w-3 h-3" />
            <span>Grid</span>
          </button>
          <button
            onClick={() => onToggleDisplayOption('showAxes')}
            className={`flex items-center space-x-1 px-2 py-1 rounded text-[11px] font-medium transition-all ${
              displayOptions.showAxes
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-700/50'
                : 'bg-slate-800/60 text-slate-400 hover:bg-slate-800'
            }`}
          >
            <Compass className="w-3 h-3" />
            <span>Axes</span>
          </button>
          <button
            onClick={() => onToggleDisplayOption('showLabels')}
            className={`flex items-center space-x-1 px-2 py-1 rounded text-[11px] font-medium transition-all ${
              displayOptions.showLabels
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-700/50'
                : 'bg-slate-800/60 text-slate-400 hover:bg-slate-800'
            }`}
          >
            <Tag className="w-3 h-3" />
            <span>Labels</span>
          </button>
          <button
            onClick={() => onToggleDisplayOption('showIncidentRay')}
            className={`flex items-center space-x-1 px-2 py-1 rounded text-[11px] font-medium transition-all ${
              displayOptions.showIncidentRay
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-700/50'
                : 'bg-slate-800/60 text-slate-400 hover:bg-slate-800'
            }`}
          >
            <Eye className="w-3 h-3" />
            <span>Incident</span>
          </button>
          <button
            onClick={() => onToggleDisplayOption('showInternalRays')}
            className={`flex items-center space-x-1 px-2 py-1 rounded text-[11px] font-medium transition-all ${
              displayOptions.showInternalRays
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-700/50'
                : 'bg-slate-800/60 text-slate-400 hover:bg-slate-800'
            }`}
          >
            <Layers className="w-3 h-3" />
            <span>Internal</span>
          </button>
          <button
            onClick={() => onToggleDisplayOption('showSpectrum')}
            className={`flex items-center space-x-1 px-2 py-1 rounded text-[11px] font-medium transition-all ${
              displayOptions.showSpectrum
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-700/50'
                : 'bg-slate-800/60 text-slate-400 hover:bg-slate-800'
            }`}
          >
            <Eye className="w-3 h-3" />
            <span>Spectrum</span>
          </button>
        </div>
      </div>
    </div>
  );
};
