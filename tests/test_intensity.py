import pytest

from ir_rb_sim.config import DEFAULT_CONFIG
from ir_rb_sim.intensity import IntensityCurve, build_intensity_curves


def test_zero_offset_curve_hits_exact_dac_bounds():
    curve = IntensityCurve(unit_index=0, offset_dac=0.0)
    assert curve.i_min(0.0) == pytest.approx(DEFAULT_CONFIG.DAC_MIN)
    assert curve.i_min(DEFAULT_CONFIG.MAX_RANGE_CM) == pytest.approx(DEFAULT_CONFIG.DAC_MAX)


def test_curve_is_monotonically_increasing_with_distance():
    curve = IntensityCurve(unit_index=0, offset_dac=0.0)
    distances = [0, 5, 10, 15, 20, 25, 30]
    i_mins = [curve.i_min(d) for d in distances]
    assert i_mins == sorted(i_mins)


def test_offset_shifts_curve_uniformly():
    base_curve = IntensityCurve(unit_index=0, offset_dac=0.0)
    shifted_curve = IntensityCurve(unit_index=1, offset_dac=50.0)
    for d in [0, 10, 20, 30]:
        assert shifted_curve.i_min(d) == pytest.approx(base_curve.i_min(d) + 50.0)


def test_build_intensity_curves_count_and_indices():
    curves = build_intensity_curves(seed=1)
    assert len(curves) == DEFAULT_CONFIG.NUM_SENSOR_UNITS
    assert [c.unit_index for c in curves] == list(range(DEFAULT_CONFIG.NUM_SENSOR_UNITS))


def test_build_intensity_curves_is_reproducible_with_seed():
    curves_a = build_intensity_curves(seed=42)
    curves_b = build_intensity_curves(seed=42)
    offsets_a = [c.offset_dac for c in curves_a]
    offsets_b = [c.offset_dac for c in curves_b]
    assert offsets_a == offsets_b


def test_build_intensity_curves_varies_across_units():
    curves = build_intensity_curves(seed=42)
    offsets = [c.offset_dac for c in curves]
    assert len(set(offsets)) > 1