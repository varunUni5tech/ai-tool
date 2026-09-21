"""Matplotlib visualization exporter for 2D plots, trajectories, and ray diagrams."""

import os
from typing import Optional
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server/CLI rendering
import matplotlib.pyplot as plt

from ai_simulation_engine.models.simulation import SimulationResult
from ai_simulation_engine.errors.exceptions import VisualizationError


class MatplotlibExporter:
    """Renders SimulationResult objects to static PNG/SVG images using Matplotlib."""

    @staticmethod
    def render_to_file(result: SimulationResult, output_path: str) -> str:
        """Render result object into image file (PNG/SVG)."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

        sim_type = result.simulation_type

        try:
            if sim_type == "function_plot":
                x = result.data.get("x", [])
                y = result.data.get("y", [])
                expr = result.metadata.get("expression", "f(x)")
                ax.plot(x, y, label=f"y = {expr}", color="#1f77b4", linewidth=2)
                ax.set_title(f"Function Plot: y = {expr}")
                ax.set_xlabel("x")
                ax.set_ylabel("y")
                ax.grid(True, linestyle="--", alpha=0.6)
                ax.legend()

            elif sim_type == "projectile_motion":
                x = result.data.get("x", [])
                y = result.data.get("y", [])
                ax.plot(x, y, color="#e377c2", linewidth=2, label="Trajectory")
                ax.fill_between(x, y, color="#e377c2", alpha=0.1)
                ax.set_title("Projectile Motion Trajectory")
                ax.set_xlabel("Horizontal Distance x (m)")
                ax.set_ylabel("Vertical Height y (m)")
                ax.set_ylim(bottom=0)
                ax.grid(True, linestyle="--", alpha=0.6)
                ax.legend()

            elif sim_type == "optical_prism":
                geom = result.data.get("geometry", {})
                vertices = geom.get("prism_vertices", [])
                ray_pts = geom.get("ray_points", [])

                # Draw Prism Triangle
                if vertices:
                    tri = plt.Polygon(vertices, closed=True, fill=True, facecolor="#a6cee3", alpha=0.4, edgecolor="#1f78b4", linewidth=2)
                    ax.add_patch(tri)

                # Draw Ray
                if len(ray_pts) >= 4:
                    px = [p[0] for p in ray_pts]
                    py = [p[1] for p in ray_pts]
                    ax.plot(px, py, color="#ff7f00", linewidth=2, marker="o", markersize=4, label="Light Ray")

                ax.set_title(f"Prism Refraction (n={result.summary.get('refractive_index')})")
                ax.set_aspect("equal")
                ax.grid(True, linestyle="--", alpha=0.4)
                ax.legend()

            elif sim_type == "prism_dispersion":
                spectral_rays = result.data.get("spectral_rays", [])
                # Draw Prism from first ray geometry
                if spectral_rays:
                    geom = spectral_rays[0].get("geometry", {})
                    vertices = geom.get("prism_vertices", [])
                    if vertices:
                        tri = plt.Polygon(vertices, closed=True, fill=True, facecolor="#e0e0e0", alpha=0.5, edgecolor="#333333", linewidth=2)
                        ax.add_patch(tri)

                    for ray in spectral_rays:
                        ray_pts = ray.get("geometry", {}).get("ray_points", [])
                        color = ray.get("color", "#ff0000")
                        wl = ray.get("wavelength_nm")
                        if len(ray_pts) >= 4:
                            px = [p[0] for p in ray_pts]
                            py = [p[1] for p in ray_pts]
                            ax.plot(px, py, color=color, linewidth=1.8, label=f"{wl:.0f} nm")

                ax.set_title("Prism White Light Dispersion Spectrum")
                ax.set_aspect("equal")
                ax.grid(True, linestyle="--", alpha=0.4)
                ax.legend(loc="upper left", fontsize=8)

            else:
                ax.text(0.5, 0.5, f"Simulation: {sim_type}", ha="center", va="center")

            plt.tight_layout()
            fig.savefig(output_path)
            plt.close(fig)
            return output_path
        except Exception as e:
            plt.close(fig)
            raise VisualizationError(f"Failed to render plot to file: {str(e)}") from e
