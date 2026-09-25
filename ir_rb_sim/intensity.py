from dataclasses import dataclass
from typing import List, Optional

import numpy as np

from .config import Config, DEFAULT_CONFIG


@dataclass(frozen=True)
class IntensityCurve:
    unit_index: int
    offset_dac: float

    def i_min(self, distance_cm: float, config: Config = DEFAULT_CONFIG) -> float:
        frac = distance_cm / config.MAX_RANGE_CM
        base = config.DAC_MIN + frac * (config.DAC_MAX - config.DAC_MIN)
        return base + self.offset_dac


def build_intensity_curves(
    config: Config = DEFAULT_CONFIG,
    seed: Optional[int] = None,
) -> List[IntensityCurve]:
    rng = np.random.default_rng(seed)
    return [
        IntensityCurve(
            unit_index=i,
            offset_dac=float(rng.normal(0.0, config.CALIBRATION_ERROR_STD_DAC)),
        )
        for i in range(config.NUM_SENSOR_UNITS)
    ]