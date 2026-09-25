"""
Robot: a simple container bundling a robot's Pose with its own sensor ring.

This is deliberately a plain data container, not the round scheduler.
Algorithm 1's per-round detection/ranging behavior (Step 8) will operate
ON Robot objects, not live inside this class - keeps "what a robot is"
separate from "what a robot does each cycle."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .config import Config, DEFAULT_CONFIG
from .geometry import Pose
from .sensor import SensorUnit, build_sensor_ring, visible_units


@dataclass
class Robot:
    id: int
    pose: Pose
    sensor_ring: List[SensorUnit] = field(default_factory=list)

    @classmethod
    def create(cls, id: int, pose: Pose, config: Config = DEFAULT_CONFIG) -> "Robot":
        """Build a Robot with a freshly-generated 8-unit sensor ring from Config."""
        return cls(id=id, pose=pose, sensor_ring=build_sensor_ring(config))

    def visible_units_to(self, other: "Robot") -> List[int]:
        """Which of THIS robot's sensor units can geometrically see `other`?"""
        return visible_units(self.pose, other.pose, self.sensor_ring)