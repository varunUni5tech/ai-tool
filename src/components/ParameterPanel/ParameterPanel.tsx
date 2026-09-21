import React from 'react';
import { Sliders } from 'lucide-react';

interface ParameterPanelProps {
  result: any;
}

export const ParameterPanel: React.FC<ParameterPanelProps> = ({ result }) => {
  if (!result) return null;

  const { parameters, summary, domain, simulation_type } = result;
  const p = parameters || {};
  const s = summary || {};

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl backdrop-blur-md">
      <div className="flex items-center space-x-2 pb-3 mb-3 border-b border-slate-800">
        <Sliders className="w-4 h-4 text-cyan-400" />
        <h3 className="text-xs font-mono font-bold tracking-wider text-slate-200 uppercase">
          Simulation Parameters & Physics Overview
        </h3>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
          <span className="text-[11px] text-slate-400 block font-mono">Domain / Type</span>
          <span className="font-semibold text-cyan-300 font-mono text-xs">
            {domain || 'optics'} / {simulation_type}
          </span>
        </div>

        {/* Projectile Motion Specific Parameters */}
        {simulation_type === 'projectile_motion' && (
          <>
            <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400 block font-mono">Initial Velocity (v₀)</span>
              <span className="font-bold text-amber-300 text-sm font-mono">
                {(p.initial_velocity ?? 20.0).toFixed(1)} m/s
              </span>
            </div>
            <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400 block font-mono">Launch Angle (θ)</span>
              <span className="font-bold text-emerald-300 text-sm font-mono">
                {(p.launch_angle ?? 45.0).toFixed(1)}°
              </span>
            </div>
            <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400 block font-mono">Gravity (g)</span>
              <span className="font-mono text-slate-200 text-xs">
                {(p.gravity ?? 9.81).toFixed(2)} m/s²
              </span>
            </div>
          </>
        )}

        {/* Function Plot Specific Parameters */}
        {simulation_type === 'function_plot' && (
          <>
            <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400 block font-mono">Function Expression</span>
              <span className="font-bold text-purple-300 text-xs font-mono">
                y = {p.expression || 'sin(x)'}
              </span>
            </div>
            <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400 block font-mono">Domain Range [Min, Max]</span>
              <span className="font-bold text-cyan-300 text-xs font-mono">
                [{p.domain?.min ?? 0}, {(p.domain?.max ?? 6.28).toFixed(2)}]
              </span>
            </div>
            <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400 block font-mono">Sampling Resolution</span>
              <span className="font-mono text-slate-200 text-xs">
                {p.domain?.samples ?? 200} grid points
              </span>
            </div>
          </>
        )}

        {/* Prism / Optics Specific Parameters */}
        {simulation_type !== 'projectile_motion' && simulation_type !== 'function_plot' && (
          <>
            <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400 block font-mono">Apex Angle (A)</span>
              <span className="font-bold text-amber-300 text-sm font-mono">
                {(p.apex_angle ?? 60.0).toFixed(1)}°
              </span>
            </div>
            <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400 block font-mono">Incident Angle (i₁)</span>
              <span className="font-bold text-emerald-300 text-sm font-mono">
                {(p.incident_angle ?? 30.0).toFixed(1)}°
              </span>
            </div>
            <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400 block font-mono">Refractive Parameters</span>
              <span className="font-mono text-slate-200 text-xs">
                {p.cauchy_b !== undefined ? `B=${p.cauchy_b}, C=${p.cauchy_c}` : `n=${p.refractive_index ?? 1.5}`}
              </span>
            </div>
          </>
        )}
      </div>

      {/* Summary Metrics Bar */}
      {simulation_type === 'projectile_motion' && s && (
        <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono text-slate-300">
          <div>
            Max Height (H_max): <span className="text-pink-400 font-bold">{s.max_height_m} m</span>
          </div>
          <div>
            Flight Time (T): <span className="text-cyan-400 font-bold">{s.flight_time_s} s</span>
          </div>
          <div>
            Horizontal Range (R): <span className="text-emerald-400 font-bold">{s.horizontal_range_m} m</span>
          </div>
        </div>
      )}

      {simulation_type !== 'projectile_motion' && simulation_type !== 'function_plot' && (
        <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono text-slate-300">
          <div>
            Angular Dispersion (Δδ): <span className="text-cyan-400 font-bold">{result.angularDispersionDeg ?? 0}°</span>
          </div>
          <div>
            Deviation Range: <span className="text-slate-400">{result.minDeviationDeg ?? 0}° – {result.maxDeviationDeg ?? 0}°</span>
          </div>
        </div>
      )}
    </div>
  );
};
