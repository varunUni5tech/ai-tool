"""Plotly 3D visualization exporter for 3D Prism Dispersion and Ray Tracing."""

import plotly.graph_objects as go
from ai_simulation_engine.models.simulation import SimulationResult
from ai_simulation_engine.errors.exceptions import VisualizationError


class Plotly3DExporter:
    """Renders 3D simulations (e.g., 3D Prism Dispersion) into interactive 3D Plotly figures."""

    @staticmethod
    def render_prism_3d_html(result: SimulationResult) -> str:
        """Render 3D Prism Dispersion or Refraction into an interactive 3D HTML plot."""
        try:
            fig = go.Figure()

            # Determine rays data
            if result.simulation_type == "prism_dispersion":
                spectral_rays = result.data.get("spectral_rays", [])
            else:
                spectral_rays = [result.data]

            if not spectral_rays:
                raise VisualizationError("No ray data found in simulation result for 3D rendering.")

            # Extract 2D geometry from first ray
            geom = spectral_rays[0].get("geometry", {})
            vertices_2d = geom.get("prism_vertices", [[-2, -1], [0, 2], [2, -1]])

            # 3D Prism Mesh Geometry (Extruded along Z axis from -2.5 to +2.5)
            z_bottom = -2.5
            z_top = 2.5

            v0_2d, v1_2d, v2_2d = vertices_2d[0], vertices_2d[1], vertices_2d[2]

            # 6 3D Vertices
            x_nodes = [v0_2d[0], v1_2d[0], v2_2d[0], v0_2d[0], v1_2d[0], v2_2d[0]]
            y_nodes = [v0_2d[1], v1_2d[1], v2_2d[1], v0_2d[1], v1_2d[1], v2_2d[1]]
            z_nodes = [z_bottom, z_bottom, z_bottom, z_top, z_top, z_top]

            # Triangulation (i, j, k indices for Mesh3d)
            # Bottom cap (0,1,2), Top cap (3,4,5)
            # Side 1 (0,1,4) & (0,4,3), Side 2 (1,2,5) & (1,5,4), Side 3 (2,0,3) & (2,3,5)
            i_faces = [0, 3, 0, 0, 1, 1, 2, 2]
            j_faces = [1, 4, 1, 4, 2, 5, 0, 3]
            k_faces = [2, 5, 4, 3, 5, 4, 3, 5]

            # Add 3D Prism Mesh (Glass Aesthetic)
            fig.add_trace(go.Mesh3d(
                x=x_nodes, y=y_nodes, z=z_nodes,
                i=i_faces, j=j_faces, k=k_faces,
                opacity=0.35,
                color="lightblue",
                flatshading=True,
                name="Glass Prism (3D)",
                showscale=False,
                lighting=dict(ambient=0.5, diffuse=0.8, specular=0.5, roughness=0.1),
            ))

            # Incident White Light Ray (3D)
            first_pts = geom.get("ray_points", [])
            if len(first_pts) >= 2:
                p0, p1 = first_pts[0], first_pts[1]
                # Draw white incident beam bundle across Z height [-0.5, 0, 0.5]
                for z_off in [-0.4, 0.0, 0.4]:
                    fig.add_trace(go.Scatter3d(
                        x=[p0[0], p1[0]],
                        y=[p0[1], p1[1]],
                        z=[z_off, z_off],
                        mode="lines",
                        line=dict(color="#FFFFFF", width=6),
                        name="Incident White Light",
                        showlegend=(z_off == 0.0)
                    ))

            # Render 3D Spectral Rays (Refracted inside & Emergent outside)
            for ray in spectral_rays:
                pts = ray.get("geometry", {}).get("ray_points", [])
                color = ray.get("color", "#FF0000")
                wl = ray.get("wavelength_nm", 600)
                n_val = ray.get("refractive_index", 1.5)

                if len(pts) >= 4:
                    p1, p2, p3 = pts[1], pts[2], pts[3]

                    # 3D Beam fan at 3 Z height levels for rich volumetric depth
                    for z_off in [-0.4, 0.0, 0.4]:
                        # Internal refracted ray
                        fig.add_trace(go.Scatter3d(
                            x=[p1[0], p2[0]],
                            y=[p1[1], p2[1]],
                            z=[z_off, z_off],
                            mode="lines",
                            line=dict(color=color, width=4),
                            showlegend=False,
                        ))

                        # Emergent dispersed ray
                        fig.add_trace(go.Scatter3d(
                            x=[p2[0], p3[0]],
                            y=[p2[1], p3[1]],
                            z=[z_off, z_off],
                            mode="lines+markers",
                            line=dict(color=color, width=5),
                            marker=dict(size=3, color=color),
                            name=f"{wl:.0f} nm (n={n_val})",
                            showlegend=(z_off == 0.0)
                        ))

            # 3D Layout configuration (Dark sci-fi aesthetic)
            fig.update_layout(
                title=dict(
                    text="3D Interactive Prism White Light Dispersion",
                    font=dict(size=20, color="#FFFFFF")
                ),
                scene=dict(
                    xaxis=dict(title="X (Distance)", backgroundcolor="#111111", gridcolor="#333333", showbackground=True),
                    yaxis=dict(title="Y (Height)", backgroundcolor="#111111", gridcolor="#333333", showbackground=True),
                    zaxis=dict(title="Z (Prism Width)", backgroundcolor="#111111", gridcolor="#333333", showbackground=True),
                    aspectmode="data",
                    camera=dict(
                        eye=dict(x=1.8, y=-1.8, z=1.2)
                    )
                ),
                paper_bgcolor="#0d0f12",
                plot_bgcolor="#0d0f12",
                legend=dict(font=dict(color="#FFFFFF"), bgcolor="rgba(0,0,0,0.5)"),
            )

            return fig.to_html(full_html=True, include_plotlyjs="cdn")
        except Exception as e:
            raise VisualizationError(f"Failed to render 3D Prism plot: {str(e)}") from e
