"""Physics simulation: Prism Single-Ray Refraction."""

import math
from typing import Dict, Any, List
from ai_simulation_engine.simulations.base import StatelessSimulation
from ai_simulation_engine.simulations.registry import SimulationRegistry
from ai_simulation_engine.models.simulation import SimulationSpec, SimulationResult
from ai_simulation_engine.models.physics import PrismRefractionSpec
from ai_simulation_engine.errors.exceptions import SimulationValidationError, SolverError


@SimulationRegistry.register(domain="optics", simulation_type="optical_prism")
class PrismRefractionSimulation(StatelessSimulation):
    """Computes ray refraction geometry through a triangular prism using Snell's Law."""

    def __init__(self, spec: SimulationSpec):
        super().__init__(spec)
        self.params: PrismRefractionSpec = None
        self.result: SimulationResult = None

    def validate(self) -> None:
        try:
            self.params = PrismRefractionSpec.model_validate(self.spec.parameters)
        except Exception as e:
            raise SimulationValidationError(f"Invalid PrismRefractionSpec parameters: {str(e)}") from e

    def initialize(self) -> None:
        self.initialized = True

    def calculate_ray_path(self, i1_deg: float, n: float, A_deg: float) -> Dict[str, Any]:
        """Compute Snell's law refraction optics for a ray entering a triangular prism."""
        A = math.radians(A_deg)
        i1 = math.radians(i1_deg)

        # Surface 1 refraction: sin(i1) = n * sin(r1)
        sin_r1 = math.sin(i1) / n
        if abs(sin_r1) > 1.0:
            raise SolverError(f"Incident angle {i1_deg}° cannot enter prism surface 1.")
        r1 = math.asin(sin_r1)

        # Geometry inside prism: r1 + r2 = A => r2 = A - r1
        r2 = A - r1

        # Critical angle check for surface 2
        critical_angle = math.asin(1.0 / n)
        is_tir = r2 > critical_angle

        if is_tir:
            i2 = None
            deviation = None
            i2_deg = None
            deviation_deg = None
        else:
            sin_i2 = n * math.sin(r2)
            i2 = math.asin(sin_i2)
            deviation = i1 + i2 - A
            i2_deg = math.degrees(i2)
            deviation_deg = math.degrees(deviation)

        # Geometric ray coordinates (Prism with apex angle A centered at origin)
        # Prism vertices
        side_len = 4.0
        h = side_len * math.cos(A / 2)
        w = 2 * side_len * math.sin(A / 2)

        apex = [0.0, h / 2]
        left_v = [-w / 2, -h / 2]
        right_v = [w / 2, -h / 2]

        # Intersection point on left face (Surface 1)
        p1 = [-w / 4, 0.0]  # Midpoint of left face

        # Ray directions
        # Face 1 normal unit vector (pointing out/up-left)
        face1_angle = math.atan2(apex[1] - left_v[1], apex[0] - left_v[0])
        normal1_angle = face1_angle + math.pi / 2
        p0 = [p1[0] - 3.0 * math.cos(normal1_angle - i1), p1[1] - 3.0 * math.sin(normal1_angle - i1)]

        # Internal ray vector to Face 2
        internal_ray_angle = face1_angle - (math.pi / 2 - r1)
        # Estimate p2 on right face
        p2 = [w / 4, 0.0]

        # Emergent ray direction
        if not is_tir:
            face2_angle = math.atan2(right_v[1] - apex[1], right_v[0] - apex[0])
            emergent_angle = face2_angle - (math.pi / 2 + i2)
            p3 = [p2[0] + 3.0 * math.cos(emergent_angle), p2[1] + 3.0 * math.sin(emergent_angle)]
        else:
            p3 = [p2[0] - 2.0, p2[1] - 2.0]

        return {
            "i1_deg": i1_deg,
            "r1_deg": math.degrees(r1),
            "r2_deg": math.degrees(r2),
            "i2_deg": i2_deg,
            "deviation_deg": deviation_deg,
            "critical_angle_deg": math.degrees(critical_angle),
            "is_total_internal_reflection": is_tir,
            "geometry": {
                "prism_vertices": [left_v, apex, right_v],
                "ray_points": [p0, p1, p2, p3],
            },
        }

    def run(self) -> SimulationResult:
        if not self.initialized:
            self.initialize()

        ray_info = self.calculate_ray_path(
            i1_deg=self.params.incident_angle,
            n=self.params.refractive_index,
            A_deg=self.params.apex_angle,
        )

        summary = {
            "apex_angle_deg": self.params.apex_angle,
            "refractive_index": self.params.refractive_index,
            "incident_angle_deg": self.params.incident_angle,
            "refracted_angle_1_deg": float(round(ray_info["r1_deg"], 4)),
            "refracted_angle_2_deg": float(round(ray_info["r2_deg"], 4)),
            "emergent_angle_deg": float(round(ray_info["i2_deg"], 4)) if ray_info["i2_deg"] is not None else "TIR",
            "deviation_angle_deg": float(round(ray_info["deviation_deg"], 4)) if ray_info["deviation_deg"] is not None else "TIR",
            "total_internal_reflection": ray_info["is_total_internal_reflection"],
        }

        self.result = SimulationResult(
            simulation_type=self.spec.simulation_type,
            domain=self.spec.domain,
            metadata={"params": self.params.model_dump()},
            summary=summary,
            data=ray_info,
            frames=[],
        )
        return self.result

    def get_results(self) -> SimulationResult:
        if self.result is None:
            return self.run()
        return self.result
