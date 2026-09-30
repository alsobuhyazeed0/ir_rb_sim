from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from .config import Config, DEFAULT_CONFIG
from .intensity import IntensityCurve
from .noise import NoiseModel, DEFAULT_NOISE_MODEL
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


def _level_rank(level: DistanceLevel) -> int:
    return 8 if level == DistanceLevel.INF else level.value


def _median_level(levels: List[DistanceLevel]) -> DistanceLevel:
    ordered = sorted(levels, key=_level_rank)
    return ordered[len(ordered) // 2]


def build_calibration_table_with_noise(
    curve: IntensityCurve,
    noise: NoiseModel = DEFAULT_NOISE_MODEL,
    rng: Optional[np.random.Generator] = None,
    config: Config = DEFAULT_CONFIG,
) -> CalibrationTable:
    if rng is None:
        rng = np.random.default_rng()

    result = CalibrationTable()

    for distance_cm in config.CALIBRATION_DISTANCES_CM:
        i_min = curve.i_min(distance_cm, config)

        levels = []
        for _ in range(config.NUM_CALIBRATION_TRIALS):
            detect_fn = noise.make_detect_fn(i_min, rng)
            levels.append(binary_search_range(detect_fn).level)

        median_level = _median_level(levels)

        if median_level == DistanceLevel.INF:
            result.unresolved_distances_cm.append(distance_cm)
        else:
            result.table[median_level] = distance_cm

    return result