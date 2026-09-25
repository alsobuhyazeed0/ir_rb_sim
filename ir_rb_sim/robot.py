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
        return cls(id=id, pose=pose, sensor_ring=build_sensor_ring(config))

    def visible_units_to(self, other: "Robot") -> List[int]:
        return visible_units(self.pose, other.pose, self.sensor_ring)