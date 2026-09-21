import React from 'react';
import { Activity } from 'lucide-react';

interface ResultsPanelProps {
  result: any;
}

export const ResultsPanel: React.FC<ResultsPanelProps> = ({ result }) => {
  if (!result) return null;

  const { simulation_type, summary, rays, parameters } = result;
  const p = parameters || {};
  const s = summary || {};

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl backdrop-blur-md">
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-mono font-bold tracking-wider text-slate-200 uppercase">
            Physics Execution Results
          </h3>
        </div>
        <span className="text-[11px] font-mono text-slate-400">
          {simulation_type === 'projectile_motion'
            ? 'Kinematics: x(t) = v₀ₓ·t, y(t) = v₀y·t - ½g·t²'
            : simulation_type === 'function_plot'
            ? `Math Expression: y = ${p.expression || 'sin(x)'}`
            : `Cauchy Equation: n(λ) = ${p.cauchy_b ?? 1.5} + ${p.cauchy_c ?? 0}/λ²`}
        </span>
      </div>

      {/* Projectile Motion Results Table */}
      {simulation_type === 'projectile_motion' && (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-[11px]">
                <th className="pb-2 font-medium">Kinematic Metric</th>
                <th className="pb-2 font-medium">Formula</th>
                <th className="pb-2 font-medium">Computed Value</th>
                <th className="pb-2 font-medium text-right">Unit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              <tr>
                <td className="py-2 font-semibold text-pink-400">Maximum Height (H_max)</td>
                <td className="py-2 text-slate-400">v₀y² / (2g)</td>
                <td className="py-2 text-amber-300 font-bold">{s.max_height_m ?? 0}</td>
                <td className="py-2 text-right text-slate-400">meters (m)</td>
              </tr>
              <tr>
                <td className="py-2 font-semibold text-cyan-400">Total Flight Time (T)</td>
                <td className="py-2 text-slate-400">2·v₀y / g</td>
                <td className="py-2 text-cyan-300 font-bold">{s.flight_time_s ?? 0}</td>
                <td className="py-2 text-right text-slate-400">seconds (s)</td>
              </tr>
              <tr>
                <td className="py-2 font-semibold text-emerald-400">Horizontal Range (R)</td>
                <td className="py-2 text-slate-400">v₀x · T</td>
                <td className="py-2 text-emerald-300 font-bold">{s.horizontal_range_m ?? 0}</td>
                <td className="py-2 text-right text-slate-400">meters (m)</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}

      {/* Function Plot Results */}
      {simulation_type === 'function_plot' && (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-[11px]">
                <th className="pb-2 font-medium">Parameter</th>
                <th className="pb-2 font-medium">Value</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              <tr>
                <td className="py-2 text-purple-400 font-semibold">Expression</td>
                <td className="py-2 text-cyan-300 font-bold">y = {p.expression || 'sin(x)'}</td>
              </tr>
              <tr>
                <td className="py-2 text-slate-400 font-semibold">Domain Range</td>
                <td className="py-2 text-amber-300 font-bold">[{s.domain_min ?? 0}, {s.domain_max ?? 6.28}]</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}

      {/* Prism / Optics Refraction Table */}
      {simulation_type !== 'projectile_motion' && simulation_type !== 'function_plot' && rays && (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-[11px]">
                <th className="pb-2 font-medium">Color</th>
                <th className="pb-2 font-medium">Wavelength (λ)</th>
                <th className="pb-2 font-medium">Refractive Index n(λ)</th>
                <th className="pb-2 font-medium">Deviation Angle (δ)</th>
                <th className="pb-2 font-medium text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {rays.map((ray: any) => (
                <tr key={ray.wavelengthNm} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-2 flex items-center space-x-2">
                    <div
                      className="w-3.5 h-3.5 rounded-full shadow-sm border border-white/20 shrink-0"
                      style={{ backgroundColor: ray.color }}
                    />
                    <span className="font-semibold text-slate-200">{ray.spectralName}</span>
                  </td>
                  <td className="py-2 text-cyan-300 font-semibold">{ray.wavelengthNm} nm</td>
                  <td className="py-2 text-amber-300 font-bold">
                    {typeof ray.refractiveIndex === 'number' ? ray.refractiveIndex.toFixed(5) : '1.50000'}
                  </td>
                  <td className="py-2 text-emerald-300 font-bold">
                    {ray.isTotalInternalReflection ? (
                      <span className="text-rose-400 font-semibold">Total Internal Reflection (TIR)</span>
                    ) : (
                      `${typeof ray.deviationAngleDeg === 'number' ? ray.deviationAngleDeg.toFixed(2) : '0.00'}°`
                    )}
                  </td>
                  <td className="py-2 text-right">
                    {ray.isTotalInternalReflection ? (
                      <span className="px-2 py-0.5 text-[10px] bg-rose-950 text-rose-400 border border-rose-800 rounded font-semibold">
                        TIR
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 text-[10px] bg-cyan-950 text-cyan-300 border border-cyan-800 rounded">
                        Refracted
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
