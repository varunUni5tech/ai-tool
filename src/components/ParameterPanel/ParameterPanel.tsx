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
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
      <div className="flex items-center space-x-2 pb-3 mb-3 border-b border-slate-200">
        <Sliders className="w-4 h-4 text-blue-600" />
        <h3 className="text-xs font-mono font-bold tracking-wider text-slate-900 uppercase">
          Simulation Parameters & Physics Overview
        </h3>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
          <span className="text-[11px] text-slate-500 block font-mono">Domain / Type</span>
          <span className="font-semibold text-blue-700 font-mono text-xs">
            {domain || 'optics'} / {simulation_type}
          </span>
        </div>

        {/* Projectile Motion Specific Parameters */}
        {simulation_type === 'projectile_motion' && (
          <>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[11px] text-slate-500 block font-mono">Initial Velocity (v₀)</span>
              <span className="font-bold text-amber-700 text-sm font-mono">
                {(p.initial_velocity ?? 20.0).toFixed(1)} m/s
              </span>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[11px] text-slate-500 block font-mono">Launch Angle (θ)</span>
              <span className="font-bold text-emerald-700 text-sm font-mono">
                {(p.launch_angle ?? 45.0).toFixed(1)}°
              </span>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[11px] text-slate-500 block font-mono">Gravity (g)</span>
              <span className="font-mono text-slate-800 text-xs">
                {(p.gravity ?? 9.81).toFixed(2)} m/s²
              </span>
            </div>
          </>
        )}

        {/* Function Plot Specific Parameters */}
        {simulation_type === 'function_plot' && (
          <>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[11px] text-slate-500 block font-mono">Function Expression</span>
              <span className="font-bold text-purple-700 text-xs font-mono">
                y = {p.expression || 'sin(x)'}
              </span>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[11px] text-slate-500 block font-mono">Domain Range [Min, Max]</span>
              <span className="font-bold text-blue-700 text-xs font-mono">
                [{p.domain?.min ?? 0}, {(p.domain?.max ?? 6.28).toFixed(2)}]
              </span>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[11px] text-slate-500 block font-mono">Sampling Resolution</span>
              <span className="font-mono text-slate-800 text-xs">
                {p.domain?.samples ?? 200} grid points
              </span>
            </div>
          </>
        )}

        {/* Orbital / Planets Specific Parameters */}
        {simulation_type === 'orbital_motion' && (
          <>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[11px] text-slate-500 block font-mono">Central Body</span>
              <span className="font-bold text-amber-700 text-sm font-mono">
                Sun (1.989e30 kg)
              </span>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[11px] text-slate-500 block font-mono">Simulated Planets</span>
              <span className="font-bold text-blue-700 text-sm font-mono">
                {s.planets_count || 6} Orbits
              </span>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[11px] text-slate-500 block font-mono">Gravitation Model</span>
              <span className="font-mono text-slate-800 text-xs">
                {s.orbital_model || 'Keplerian Central Force'}
              </span>
            </div>
          </>
        )}

        {/* Prism / Optics Specific Parameters */}
        {simulation_type !== 'projectile_motion' && simulation_type !== 'function_plot' && simulation_type !== 'orbital_motion' && (
          <>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[11px] text-slate-500 block font-mono">Apex Angle (A)</span>
              <span className="font-bold text-amber-700 text-sm font-mono">
                {(p.apex_angle ?? 60.0).toFixed(1)}°
              </span>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[11px] text-slate-500 block font-mono">Incident Angle (i₁)</span>
              <span className="font-bold text-emerald-700 text-sm font-mono">
                {(p.incident_angle ?? 30.0).toFixed(1)}°
              </span>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[11px] text-slate-500 block font-mono">Refractive Parameters</span>
              <span className="font-mono text-slate-800 text-xs">
                {p.cauchy_b !== undefined ? `B=${p.cauchy_b}, C=${p.cauchy_c}` : `n=${p.refractive_index ?? 1.5}`}
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
