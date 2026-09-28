import numpy as np
import pytest

from ir_rb_sim.intensity import IntensityCurve
from ir_rb_sim.noise import NoiseModel
from ir_rb_sim.ranging import binary_search_range, make_ideal_detect_fn


def test_zero_noise_matches_ideal_detect_fn_exactly():
    curve = IntensityCurve(unit_index=0, offset_dac=0.0)
    i_min = curve.i_min(22.0)

    zero_noise = NoiseModel(
        ambient_noise_std_dac=0.0, miss_detection_prob=0.0, false_positive_prob=0.0
    )
    rng = np.random.default_rng(1)

    ideal_result = binary_search_range(make_ideal_detect_fn(i_min))
    noisy_result = binary_search_range(zero_noise.make_detect_fn(i_min, rng))

    assert ideal_result.level == noisy_result.level
    assert ideal_result.trace == noisy_result.trace


def test_from_config_uses_config_values():
    from ir_rb_sim.config import DEFAULT_CONFIG

    model = NoiseModel.from_config(DEFAULT_CONFIG)
    assert model.ambient_noise_std_dac == DEFAULT_CONFIG.AMBIENT_NOISE_STD_DAC
    assert model.miss_detection_prob == DEFAULT_CONFIG.MISS_DETECTION_PROB
    assert model.false_positive_prob == DEFAULT_CONFIG.FALSE_POSITIVE_PROB


def test_full_miss_probability_always_flips_genuine_hits():
    always_miss = NoiseModel(
        ambient_noise_std_dac=0.0, miss_detection_prob=1.0, false_positive_prob=0.0
    )
    rng = np.random.default_rng(0)
    detect_fn = always_miss.make_detect_fn(i_min=1000.0, rng=rng)

    # dac_value well above i_min -> genuine hit -> must always be forced to miss
    assert all(detect_fn(2000.0) is False for _ in range(20))


def test_full_false_positive_probability_always_flips_genuine_misses():
    always_fp = NoiseModel(
        ambient_noise_std_dac=0.0, miss_detection_prob=0.0, false_positive_prob=1.0
    )
    rng = np.random.default_rng(0)
    detect_fn = always_fp.make_detect_fn(i_min=2000.0, rng=rng)

    # dac_value well below i_min -> genuine miss -> must always be forced to hit
    assert all(detect_fn(500.0) is True for _ in range(20))


def test_repeated_trials_scatter_around_true_level():
    from ir_rb_sim.config import DEFAULT_CONFIG
    from ir_rb_sim.ranging import DistanceLevel

    curve = IntensityCurve(unit_index=0, offset_dac=0.0)
    i_min = curve.i_min(22.0)  # true level = L6, per the deterministic case
    noise = NoiseModel.from_config(DEFAULT_CONFIG)
    rng = np.random.default_rng(42)

    levels = []
    for _ in range(200):
        detect_fn = noise.make_detect_fn(i_min, rng)
        levels.append(binary_search_range(detect_fn).level)

    l6_fraction = levels.count(DistanceLevel.L6) / len(levels)
    assert l6_fraction > 0.7  # majority should still land on the true level


def test_same_seed_is_reproducible():
    curve = IntensityCurve(unit_index=0, offset_dac=0.0)
    i_min = curve.i_min(22.0)
    noise = NoiseModel.from_config()

    rng_a = np.random.default_rng(7)
    rng_b = np.random.default_rng(7)

    result_a = binary_search_range(noise.make_detect_fn(i_min, rng_a))
    result_b = binary_search_range(noise.make_detect_fn(i_min, rng_b))

    assert result_a.level == result_b.level
    assert result_a.trace == result_b.trace