import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from .config import Config, DEFAULT_CONFIG
from .geometry import relative_bearing_and_distance
from .intensity import IntensityCurve, build_intensity_curves
from .noise import NoiseModel, DEFAULT_NOISE_MODEL
from .ranging import DetectFn, DistanceLevel, binary_search_range, make_ideal_detect_fn
from .robot import Robot
from .scheduler import CycleResult


@dataclass
class WorldRobot:
    robot: Robot
    intensity_curves: List[IntensityCurve]

    @classmethod
    def create(
        cls,
        id: int,
        pose,
        config: Config = DEFAULT_CONFIG,
        seed: Optional[int] = None,
    ) -> "WorldRobot":
        return cls(
            robot=Robot.create(id=id, pose=pose, config=config),
            intensity_curves=build_intensity_curves(config, seed=seed),
        )


@dataclass
class World:
    robots: List[WorldRobot]
    config: Config = field(default_factory=lambda: DEFAULT_CONFIG)
    noise: NoiseModel = field(default_factory=lambda: DEFAULT_NOISE_MODEL)
    rng: np.random.Generator = field(default_factory=np.random.default_rng)
    py_rng: random.Random = field(default_factory=random.Random)

    def _closest_neighbor_distance(
        self, observer: WorldRobot, unit_index: int
    ) -> Optional[float]:
        best: Optional[float] = None
        for other in self.robots:
            if other.robot.id == observer.robot.id:
                continue
            seen = observer.robot.visible_units_to(other.robot)
            if unit_index not in seen:
                continue
            _, distance_cm = relative_bearing_and_distance(
                observer.robot.pose, other.robot.pose
            )
            if best is None or distance_cm < best:
                best = distance_cm
        return best

    def _build_detect_fns(self, wr: WorldRobot) -> List[DetectFn]:
        n = self.config.NUM_SENSOR_UNITS
        fns: List[DetectFn] = []
        for u in range(n):
            distance_cm = self._closest_neighbor_distance(wr, u)
            if distance_cm is None:
                fns.append(make_ideal_detect_fn(self.config.DAC_MAX + 1))
            else:
                curve = wr.intensity_curves[u]
                i_min = curve.i_min(distance_cm, self.config)
                fns.append(self.noise.make_detect_fn(i_min, self.rng))
        return fns

    def _reciprocal_signal_map(
        self, transmissions: Dict[int, int]
    ) -> Dict[int, List[bool]]:
        n = self.config.NUM_SENSOR_UNITS
        sr: Dict[int, List[bool]] = {
            wr.robot.id: [False] * n for wr in self.robots
        }
        by_id = {wr.robot.id: wr for wr in self.robots}

        for transmitter_id, tx_unit in transmissions.items():
            transmitter = by_id[transmitter_id]
            for receiver in self.robots:
                if receiver.robot.id == transmitter_id:
                    continue
                # Does the transmitter's chosen unit actually aim at the
                # receiver?
                tx_sees_rx = transmitter.robot.visible_units_to(receiver.robot)
                if tx_unit not in tx_sees_rx:
                    continue
                # Which of the receiver's own units face back at the
                # transmitter?
                rx_sees_tx = receiver.robot.visible_units_to(transmitter.robot)
                for u in rx_sees_tx:
                    sr[receiver.robot.id][u] = True
        return sr

    def step(self) -> Dict[int, CycleResult]:
        n = self.config.NUM_SENSOR_UNITS
        detect_fns = {wr.robot.id: self._build_detect_fns(wr) for wr in self.robots}

        completed = {wr.robot.id: [False] * n for wr in self.robots}
        levels = {wr.robot.id: [DistanceLevel.INF] * n for wr in self.robots}
        detected = {wr.robot.id: [False] * n for wr in self.robots}
        remaining = {wr.robot.id: n for wr in self.robots}

        order = [wr.robot.id for wr in self.robots]
        by_id = {wr.robot.id: wr for wr in self.robots}

        for round_index in range(self.config.ROUNDS_PER_PHASE1):
            # Pass A: each robot (visited in random order) picks which unit
            # it would use this round, based only on its own prior state.
            self.py_rng.shuffle(order)
            transmissions: Dict[int, int] = {}
            for rid in order:
                if remaining[rid] == 0:
                    continue
                start = self.py_rng.randint(0, n - 1)
                for i in range(n):
                    u = (start + i) % n
                    if not completed[rid][u]:
                        transmissions[rid] = u
                        break

            # Pass B: resolve real signal-present state now that every
            # robot's choice for this round is fixed.
            sr = self._reciprocal_signal_map(transmissions)
            for rid in order:
                for u in range(n):
                    if sr[rid][u]:
                        detected[rid][u] = True

            for rid, chosen_unit in transmissions.items():
                if sr[rid][chosen_unit]:
                    # Collision: another robot's transmission landed on the
                    # same unit this round - defer, exactly as Algorithm 1
                    # skips ranging on a unit with an incoming signal.
                    continue
                result = binary_search_range(detect_fns[rid][chosen_unit])
                levels[rid][chosen_unit] = result.level
                completed[rid][chosen_unit] = True
                remaining[rid] -= 1

        # Phase 2: detection-only listening. Every robot that still has a
        # spare unit "idles" one - reuse whichever units are already
        # completed as passive listeners isn't meaningful here, so we just
        # check reciprocal visibility on ALL units for whichever unit(s)
        # any robot happens to still be transmitting from (any remaining
        # robot with incomplete units picks one more candidate, matching
        # Phase 1's Pass A/Pass B shape but without performing ranging).
        transmissions = {}
        for rid in order:
            if remaining[rid] == 0:
                continue
            start = self.py_rng.randint(0, n - 1)
            for i in range(n):
                u = (start + i) % n
                if not completed[rid][u]:
                    transmissions[rid] = u
                    break
        sr = self._reciprocal_signal_map(transmissions)
        for rid in order:
            for u in range(n):
                if sr[rid][u]:
                    detected[rid][u] = True

        return {
            rid: CycleResult(levels=levels[rid], detected=detected[rid])
            for rid in (wr.robot.id for wr in self.robots)
        }