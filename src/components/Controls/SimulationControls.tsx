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
    <div className="flex flex-col space-y-3 bg-white border border-slate-200 p-4 rounded-xl shadow-sm">
      {/* Animation Playback Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div className="flex items-center space-x-2">
          <button
            onClick={onPlayPause}
            className={`flex items-center space-x-2 px-4 py-1.5 rounded-lg font-semibold text-xs transition-all shadow-sm active:scale-95 cursor-pointer ${
              isPlaying
                ? 'bg-amber-600 hover:bg-amber-700 text-white'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
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
            className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-300 rounded-lg transition-all cursor-pointer"
            title="Reset Animation"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
        </div>

        {/* Speed Slider */}
        <div className="flex items-center space-x-2 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200">
          <Sliders className="w-3.5 h-3.5 text-blue-600" />
          <span className="text-xs font-mono text-slate-600">Speed:</span>
          <input
            type="range"
            min="0.2"
            max="3.0"
            step="0.1"
            value={speed}
            onChange={(e) => onSpeedChange(parseFloat(e.target.value))}
            className="w-20 accent-blue-600 cursor-pointer h-1.5 bg-slate-200 rounded-lg"
          />
          <span className="text-xs font-mono font-semibold text-blue-700 w-8 text-right">
            {speed.toFixed(1)}x
          </span>
        </div>
      </div>

      {/* Camera Views & Display Toggles */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
        {/* Camera Preset Buttons */}
        <div className="flex items-center space-x-1">
          <span className="text-slate-500 font-mono text-[11px] mr-1">Camera:</span>
          <button
            onClick={() => onSetCameraView('default')}
            className="px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-[11px] border border-slate-200 transition-all cursor-pointer font-medium"
          >
            Reset Camera
          </button>
          <button
            onClick={() => onSetCameraView('top')}
            className="px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-[11px] border border-slate-200 transition-all cursor-pointer font-medium"
          >
            Top View
          </button>
          <button
            onClick={() => onSetCameraView('front')}
            className="px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-[11px] border border-slate-200 transition-all cursor-pointer font-medium"
          >
            Front View
          </button>
          <button
            onClick={() => onSetCameraView('side')}
            className="px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-[11px] border border-slate-200 transition-all cursor-pointer font-medium"
          >
            Side View
          </button>
        </div>

        {/* Visibility Toggles */}
        <div className="flex flex-wrap items-center gap-1.5">
          <button
            onClick={() => onToggleDisplayOption('showGrid')}
            className={`flex items-center space-x-1 px-2 py-1 rounded text-[11px] font-medium transition-all cursor-pointer ${
              displayOptions.showGrid
                ? 'bg-blue-50 text-blue-700 border border-blue-300 font-semibold'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-200'
            }`}
          >
            <GridIcon className="w-3 h-3" />
            <span>Grid</span>
          </button>
          <button
            onClick={() => onToggleDisplayOption('showAxes')}
            className={`flex items-center space-x-1 px-2 py-1 rounded text-[11px] font-medium transition-all cursor-pointer ${
              displayOptions.showAxes
                ? 'bg-blue-50 text-blue-700 border border-blue-300 font-semibold'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-200'
            }`}
          >
            <Compass className="w-3 h-3" />
            <span>Axes</span>
          </button>
          <button
            onClick={() => onToggleDisplayOption('showLabels')}
            className={`flex items-center space-x-1 px-2 py-1 rounded text-[11px] font-medium transition-all cursor-pointer ${
              displayOptions.showLabels
                ? 'bg-blue-50 text-blue-700 border border-blue-300 font-semibold'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-200'
            }`}
          >
            <Tag className="w-3 h-3" />
            <span>Labels</span>
          </button>
          <button
            onClick={() => onToggleDisplayOption('showIncidentRay')}
            className={`flex items-center space-x-1 px-2 py-1 rounded text-[11px] font-medium transition-all cursor-pointer ${
              displayOptions.showIncidentRay
                ? 'bg-blue-50 text-blue-700 border border-blue-300 font-semibold'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-200'
            }`}
          >
            <Eye className="w-3 h-3" />
            <span>Incident</span>
          </button>
          <button
            onClick={() => onToggleDisplayOption('showInternalRays')}
            className={`flex items-center space-x-1 px-2 py-1 rounded text-[11px] font-medium transition-all cursor-pointer ${
              displayOptions.showInternalRays
                ? 'bg-blue-50 text-blue-700 border border-blue-300 font-semibold'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-200'
            }`}
          >
            <Layers className="w-3 h-3" />
            <span>Internal</span>
          </button>
          <button
            onClick={() => onToggleDisplayOption('showSpectrum')}
            className={`flex items-center space-x-1 px-2 py-1 rounded text-[11px] font-medium transition-all cursor-pointer ${
              displayOptions.showSpectrum
                ? 'bg-blue-50 text-blue-700 border border-blue-300 font-semibold'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-200'
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
