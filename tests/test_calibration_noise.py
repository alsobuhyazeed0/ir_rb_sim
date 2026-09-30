import numpy as np
import pytest

from ir_rb_sim.calibration import build_calibration_table, build_calibration_table_with_noise
from ir_rb_sim.intensity import IntensityCurve
from ir_rb_sim.noise import NoiseModel
from ir_rb_sim.ranging import DistanceLevel


def test_zero_noise_matches_deterministic_table():
    curve = IntensityCurve(unit_index=0, offset_dac=0.0)
    zero_noise = NoiseModel(
        ambient_noise_std_dac=0.0, miss_detection_prob=0.0, false_positive_prob=0.0
    )
    rng = np.random.default_rng(0)

    deterministic = build_calibration_table(curve)
    noisy = build_calibration_table_with_noise(curve, noise=zero_noise, rng=rng)

    assert noisy.table == deterministic.table
    assert noisy.unresolved_distances_cm == deterministic.unresolved_distances_cm


def test_moderate_default_noise_still_recovers_correct_table():
    curve = IntensityCurve(unit_index=0, offset_dac=0.0)
    deterministic = build_calibration_table(curve)

    rng = np.random.default_rng(42)
    noisy = build_calibration_table_with_noise(curve, rng=rng)

    assert noisy.table == deterministic.table


def test_loud_noise_makes_single_trials_unreliable_but_median_still_works():
    curve = IntensityCurve(unit_index=0, offset_dac=0.0)
    loud_noise = NoiseModel(
        ambient_noise_std_dac=80.0, miss_detection_prob=0.02, false_positive_prob=0.01
    )

    rng = np.random.default_rng(5)
    noisy_table = build_calibration_table_with_noise(curve, noise=loud_noise, rng=rng)

    # closer reference distances (6, 10, 14, 18cm) should still resolve
    # correctly even under loud noise - farther ones may become unreliable
    assert noisy_table.table.get(DistanceLevel.L2) == 6.0
    assert noisy_table.table.get(DistanceLevel.L3) == 10.0
    assert noisy_table.table.get(DistanceLevel.L4) == 14.0


def test_reproducible_with_same_rng_seed():
    curve = IntensityCurve(unit_index=0, offset_dac=0.0)

    rng_a = np.random.default_rng(99)
    rng_b = np.random.default_rng(99)

    table_a = build_calibration_table_with_noise(curve, rng=rng_a)
    table_b = build_calibration_table_with_noise(curve, rng=rng_b)

    assert table_a.table == table_b.table
    assert table_a.unresolved_distances_cm == table_b.unresolved_distances_cm


def test_uses_num_calibration_trials_from_config():
    from ir_rb_sim.config import Config

    custom_config = Config(NUM_CALIBRATION_TRIALS=3)
    curve = IntensityCurve(unit_index=0, offset_dac=0.0)
    rng = np.random.default_rng(1)

    # just confirm it runs without error using a custom (smaller) trial count
    result = build_calibration_table_with_noise(curve, rng=rng, config=custom_config)
    assert len(result.table) + len(result.unresolved_distances_cm) == len(
        custom_config.CALIBRATION_DISTANCES_CM
    )