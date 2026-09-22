"""Reusable core physics primitives (Vector3D, Particle, Body, Force, Gravity, Spring)."""

import math
from typing import List, Tuple, Optional


class Vector3D:
    """3D Mathematical Vector with utility methods."""

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def to_list(self) -> List[float]:
        return [self.x, self.y, self.z]

    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self) -> "Vector3D":
        mag = self.magnitude()
        if mag == 0:
            return Vector3D(0.0, 0.0, 0.0)
        return Vector3D(self.x / mag, self.y / mag, self.z / mag)

    def add(self, v: "Vector3D") -> "Vector3D":
        return Vector3D(self.x + v.x, self.y + v.y, self.z + v.z)

    def scale(self, factor: float) -> "Vector3D":
        return Vector3D(self.x * factor, self.y * factor, self.z * factor)


class Particle:
    """Physical Point Mass representation."""

    def __init__(
        self,
        name: str = "particle",
        mass: float = 1.0,
        position: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        color: str = "#00F0FF",
    ):
        self.name = name
        self.mass = float(mass)
        self.position = Vector3D(*position)
        self.velocity = Vector3D(*velocity)
        self.acceleration = Vector3D(0.0, 0.0, 0.0)
        self.color = color


class Body(Particle):
    """Extended Rigid Body with radius and moment properties."""

    def __init__(
        self,
        name: str = "body",
        mass: float = 1.0,
        radius: float = 1.0,
        position: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        color: str = "#FF9900",
    ):
        super().__init__(name=name, mass=mass, position=position, velocity=velocity, color=color)
        self.radius = float(radius)


class GravityForce:
    """Universal Gravitation Force generator between two bodies."""

    G: float = 6.67430e-11

    @classmethod
    def compute(cls, body1: Body, body2: Body) -> Vector3D:
        """Compute gravitational force exerted on body2 by body1."""
        dx = body1.position.x - body2.position.x
        dy = body1.position.y - body2.position.y
        dz = body1.position.z - body2.position.z
        r_sq = dx**2 + dy**2 + dz**2
        r = math.sqrt(r_sq)
        if r == 0:
            return Vector3D(0.0, 0.0, 0.0)

        force_mag = (cls.G * body1.mass * body2.mass) / r_sq
        return Vector3D((dx / r) * force_mag, (dy / r) * force_mag, (dz / r) * force_mag)
