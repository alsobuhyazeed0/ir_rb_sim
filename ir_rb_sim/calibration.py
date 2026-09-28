from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .config import Config, DEFAULT_CONFIG
from .intensity import IntensityCurve
from .ranging import DistanceLevel, binary_search_range, make_ideal_detect_fn


@dataclass
class CalibrationTable:
    table: Dict[DistanceLevel, float] = field(default_factory=dict)
    unresolved_distances_cm: List[float] = field(default_factory=list)

    def estimate_distance_cm(self, level: DistanceLevel) -> Optional[float]:
        return self.table.get(level)


def build_calibration_table(
    curve: IntensityCurve,
    config: Config = DEFAULT_CONFIG,
) -> CalibrationTable:
    result = CalibrationTable()

    for distance_cm in config.CALIBRATION_DISTANCES_CM:
        i_min = curve.i_min(distance_cm, config)
        ranging_result = binary_search_range(make_ideal_detect_fn(i_min))
        level = ranging_result.level

        if level == DistanceLevel.INF:
            result.unresolved_distances_cm.append(distance_cm)
        else:
            result.table[level] = distance_cm

    return result