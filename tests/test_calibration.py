import pytest

from ir_rb_sim.calibration import build_calibration_table
from ir_rb_sim.intensity import IntensityCurve
from ir_rb_sim.ranging import DistanceLevel


def test_zero_offset_curve_produces_expected_table():
    curve = IntensityCurve(unit_index=0, offset_dac=0.0)
    cal = build_calibration_table(curve)

    assert cal.table == {
        DistanceLevel.L2: 6.0,
        DistanceLevel.L3: 10.0,
        DistanceLevel.L4: 14.0,
        DistanceLevel.L5: 18.0,
        DistanceLevel.L6: 22.0,
        DistanceLevel.L7: 26.0,
    }
    assert cal.unresolved_distances_cm == [30.0]


def test_estimate_distance_cm_returns_calibrated_value():
    curve = IntensityCurve(unit_index=0, offset_dac=0.0)
    cal = build_calibration_table(curve)
    assert cal.estimate_distance_cm(DistanceLevel.L6) == pytest.approx(22.0)


def test_estimate_distance_cm_returns_none_for_unobserved_level():
    curve = IntensityCurve(unit_index=0, offset_dac=0.0)
    cal = build_calibration_table(curve)
    assert cal.estimate_distance_cm(DistanceLevel.L1) is None


def test_estimate_distance_cm_returns_none_for_inf():
    curve = IntensityCurve(unit_index=0, offset_dac=0.0)
    cal = build_calibration_table(curve)
    assert cal.estimate_distance_cm(DistanceLevel.INF) is None


def test_different_units_can_calibrate_differently():
    curve_a = IntensityCurve(unit_index=0, offset_dac=0.0)
    curve_b = IntensityCurve(unit_index=1, offset_dac=150.0)

    cal_a = build_calibration_table(curve_a)
    cal_b = build_calibration_table(curve_b)

    assert cal_a.table != cal_b.table