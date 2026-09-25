from dataclasses import dataclass, field
from enum import IntEnum
from typing import Callable, List, Tuple

from .config import DEFAULT_CONFIG


class DistanceLevel(IntEnum):
    L1 = 1
    L2 = 2
    L3 = 3
    L4 = 4
    L5 = 5
    L6 = 6
    L7 = 7
    INF = 0  # no detectable object within the 30 cm sensing range


_step = (DEFAULT_CONFIG.DAC_MAX - DEFAULT_CONFIG.DAC_MIN) / 8  # = 125
LEVEL_TEST_DAC = {
    n: DEFAULT_CONFIG.DAC_MIN + n * _step for n in range(1, 8)
}  # L1..L7 -> DAC


DetectFn = Callable[[float], bool]  # given a DAC intensity, returns hit/miss


@dataclass
class RangingResult:
    level: DistanceLevel
    trace: List[Tuple[int, float, bool]] = field(default_factory=list)


def binary_search_range(detect_fn: DetectFn) -> RangingResult:
    trace: List[Tuple[int, float, bool]] = []

    def test(level_id: int) -> bool:
        dac = LEVEL_TEST_DAC[level_id]
        hit = detect_fn(dac)
        trace.append((level_id, dac, hit))
        return hit

    hit_l4 = test(4)

    if hit_l4:
        hit_l2 = test(2)
        if hit_l2:
            leaf = DistanceLevel.L1 if test(1) else DistanceLevel.L2
        else:
            leaf = DistanceLevel.L3 if test(3) else DistanceLevel.L4
    else:
        hit_l6 = test(6)
        if hit_l6:
            leaf = DistanceLevel.L5 if test(5) else DistanceLevel.L6
        else:
            leaf = DistanceLevel.L7 if test(7) else DistanceLevel.INF

    return RangingResult(level=leaf, trace=trace)


def make_ideal_detect_fn(i_min: float) -> DetectFn:
    def detect(dac_value: float) -> bool:
        return dac_value >= i_min

    return detect