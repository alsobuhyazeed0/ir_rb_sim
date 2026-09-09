from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class Config:
    NUM_SENSOR_UNITS: int = 8
    SENSOR_SPACING_DEG: float = 45.0
    SECTOR_HALF_ANGLE_DEG: float = 22.5
    MAX_RANGE_CM: float = 30.0
    ROBOT_DIAMETER_CM: float = 14.4

    DAC_MIN: int = 800
    DAC_MAX: int = 1800
    DAC_BITS: int = 12

    BINARY_SEARCH_DEPTH: int = 3
    NUM_DISTANCE_LEVELS: int = 7

    CALIBRATION_DISTANCES_CM: List[float] = field(
        default_factory=lambda: [6.0, 10.0, 14.0, 18.0, 22.0, 26.0, 30.0]
    )

    CYCLE_DURATION_MS: float = 100.0
    PHASE1_DURATION_MS: float = 50.0
    PHASE2_DURATION_MS: float = 50.0
    ROUNDS_PER_PHASE1: int = 8
    DETECTION_WINDOW_MS: float = 1.0

    # ASSUMED: simulator noise parameters; refine during validation.
    CALIBRATION_ERROR_STD_DAC: float = 15.0
    AMBIENT_NOISE_STD_DAC: float = 10.0
    MISS_DETECTION_PROB: float = 0.02
    FALSE_POSITIVE_PROB: float = 0.01

    # Paper validation targets.
    TARGET_SINGLE_RANGE_ERROR_PCT: float = 4.75
    TARGET_SINGLE_BEARING_ERROR_DEG: float = 5.4
    TARGET_MULTI_RANGE_ERROR_PCT: float = 10.97
    TARGET_MULTI_BEARING_ERROR_DEG: float = 8.34


DEFAULT_CONFIG = Config()