import random
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from .config import Config, DEFAULT_CONFIG
from .ranging import DetectFn, DistanceLevel, binary_search_range

SignalPresentFn = Callable[[int, int], bool]


@dataclass
class CycleResult:
    levels: List[DistanceLevel] = field(default_factory=list)
    detected: List[bool] = field(default_factory=list)


def run_sensing_cycle(
    detect_fns: List[DetectFn],
    signal_present_fn: SignalPresentFn,
    config: Config = DEFAULT_CONFIG,
    rng: Optional[random.Random] = None,
) -> CycleResult:
    if rng is None:
        rng = random.Random()

    n = config.NUM_SENSOR_UNITS
    completed = [False] * n
    levels: List[DistanceLevel] = [DistanceLevel.INF] * n
    detected = [False] * n
    remaining = n

    # Phase 1: ROUNDS_PER_PHASE1 rounds, each = 1ms detection + conditional ranging
    for round_index in range(config.ROUNDS_PER_PHASE1):
        sr = [signal_present_fn(u, round_index) for u in range(n)]
        for u in range(n):
            if sr[u]:
                detected[u] = True

        if remaining > 0:
            start = rng.randint(0, n - 1)
            for i in range(n):
                u = (start + i) % n
                if not completed[u] and not sr[u]:
                    result = binary_search_range(detect_fns[u])
                    levels[u] = result.level
                    completed[u] = True
                    remaining -= 1
                    break

    # Phase 2: detection-only listening (modeled as one additional check,
    # per the note above)
    phase2_round = config.ROUNDS_PER_PHASE1
    sr_phase2 = [signal_present_fn(u, phase2_round) for u in range(n)]
    for u in range(n):
        if sr_phase2[u]:
            detected[u] = True

    return CycleResult(levels=levels, detected=detected)