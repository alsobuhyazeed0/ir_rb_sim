from dataclasses import dataclass
from typing import List

from .config import Config, DEFAULT_CONFIG
from .geometry import Pose, angular_diff_deg, relative_bearing_and_distance


@dataclass(frozen=True)
class SensorUnit:
    index: int                 # 0-7
    heading_offset_deg: float
    sector_half_angle_deg: float
    max_range_cm: float

    def in_sector(self, relative_bearing_deg: float) -> bool:
        diff = abs(angular_diff_deg(relative_bearing_deg, self.heading_offset_deg))
        return diff <= self.sector_half_angle_deg

    def in_range(self, distance_cm: float) -> bool:
        return 0.0 <= distance_cm <= self.max_range_cm

    def can_detect(self, relative_bearing_deg: float, distance_cm: float) -> bool:
        return self.in_range(distance_cm) and self.in_sector(relative_bearing_deg)

def build_sensor_ring(config: Config = DEFAULT_CONFIG) -> List[SensorUnit]:
    return [
        SensorUnit(
            index=i,
            heading_offset_deg=i * config.SENSOR_SPACING_DEG,
            sector_half_angle_deg=config.SECTOR_HALF_ANGLE_DEG,
            max_range_cm=config.MAX_RANGE_CM,
        )
        for i in range(config.NUM_SENSOR_UNITS)
    ]

def visible_units(
    observer: Pose,
    target: Pose,
    sensor_ring: List[SensorUnit],
) -> List[int]:
    bearing, distance = relative_bearing_and_distance(observer, target)
    return [unit.index for unit in sensor_ring if unit.can_detect(bearing, distance)]