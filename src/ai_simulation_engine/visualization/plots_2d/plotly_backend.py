"""Plotly interactive HTML visualization backend."""

import plotly.graph_objects as go
from ai_simulation_engine.models.simulation import SimulationResult
from ai_simulation_engine.errors.exceptions import VisualizationError


class PlotlyExporter:
    """Renders SimulationResult into interactive Plotly HTML or JSON figures."""

    @staticmethod
    def render_to_html(result: SimulationResult) -> str:
        """Render result object into a standalone interactive HTML string."""
        sim_type = result.simulation_type
        fig = go.Figure()

        try:
            if sim_type == "function_plot":
                x = result.data.get("x", [])
                y = result.data.get("y", [])
                expr = result.metadata.get("expression", "f(x)")
                fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=f"y = {expr}", line=dict(color="#1f77b4", width=3)))
                fig.update_layout(
                    title=f"Function Plot: y = {expr}",
                    xaxis_title="x",
                    yaxis_title="y",
                    template="plotly_dark",
                )

            elif sim_type == "projectile_motion":
                x = result.data.get("x", [])
                y = result.data.get("y", [])
                fig.add_trace(go.Scatter(
                    x=x, y=y, mode="lines+markers", name="Trajectory",
                    line=dict(color="#e377c2", width=3),
                    marker=dict(size=4),
                    fill="tozeroy",
                ))
                fig.update_layout(
                    title=f"Projectile Motion Trajectory (v0={result.summary.get('initial_velocity')} m/s, {result.summary.get('launch_angle_deg')}°)",
                    xaxis_title="Horizontal Distance x (m)",
                    yaxis_title="Vertical Height y (m)",
                    template="plotly_dark",
                )

            elif sim_type == "optical_prism":
                geom = result.data.get("geometry", {})
                vertices = geom.get("prism_vertices", [])
                ray_pts = geom.get("ray_points", [])

                if vertices:
                    vx = [v[0] for v in vertices] + [vertices[0][0]]
                    vy = [v[1] for v in vertices] + [vertices[0][1]]
                    fig.add_trace(go.Scatter(x=vx, y=vy, fill="toself", fillcolor="rgba(166,206,227,0.4)", line=dict(color="#1f78b4", width=2), name="Prism"))

                if len(ray_pts) >= 4:
                    px = [p[0] for p in ray_pts]
                    py = [p[1] for p in ray_pts]
                    fig.add_trace(go.Scatter(x=px, y=py, mode="lines+markers", line=dict(color="#ff7f00", width=3), name="Light Ray"))

                fig.update_layout(
                    title=f"Prism Refraction (n={result.summary.get('refractive_index')})",
                    xaxis_title="x", yaxis_title="y",
                    template="plotly_dark",
                    yaxis=dict(scaleanchor="x", scaleratio=1),
                )

            elif sim_type == "prism_dispersion":
                spectral_rays = result.data.get("spectral_rays", [])
                if spectral_rays:
                    geom = spectral_rays[0].get("geometry", {})
                    vertices = geom.get("prism_vertices", [])
                    if vertices:
                        vx = [v[0] for v in vertices] + [vertices[0][0]]
                        vy = [v[1] for v in vertices] + [vertices[0][1]]
                        fig.add_trace(go.Scatter(x=vx, y=vy, fill="toself", fillcolor="rgba(220,220,220,0.4)", line=dict(color="#666666", width=2), name="Prism"))

                    for ray in spectral_rays:
                        ray_pts = ray.get("geometry", {}).get("ray_points", [])
                        color = ray.get("color", "#ff0000")
                        wl = ray.get("wavelength_nm")
                        if len(ray_pts) >= 4:
                            px = [p[0] for p in ray_pts]
                            py = [p[1] for p in ray_pts]
                            fig.add_trace(go.Scatter(x=px, y=py, mode="lines", line=dict(color=color, width=2.5), name=f"{wl:.0f} nm"))

                fig.update_layout(
                    title="Prism White Light Dispersion Spectrum",
                    xaxis_title="x", yaxis_title="y",
                    template="plotly_dark",
                    yaxis=dict(scaleanchor="x", scaleratio=1),
                )

            return fig.to_html(full_html=True, include_plotlyjs="cdn")
        except Exception as e:
            raise VisualizationError(f"Failed to generate Plotly HTML figure: {str(e)}") from e
