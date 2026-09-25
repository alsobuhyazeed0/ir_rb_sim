import pytest

from ir_rb_sim.config import DEFAULT_CONFIG
from ir_rb_sim.ranging import (
    DistanceLevel,
    LEVEL_TEST_DAC,
    binary_search_range,
    make_ideal_detect_fn,
)


def test_paper_worked_example_L6():
    i_min = LEVEL_TEST_DAC[6]
    result = binary_search_range(make_ideal_detect_fn(i_min))

    assert result.level == DistanceLevel.L6
    assert [t[0] for t in result.trace] == [4, 6, 5]
    assert [t[2] for t in result.trace] == [False, True, False]


@pytest.mark.parametrize("level", list(DistanceLevel))
def test_every_leaf_reachable(level):
    if level == DistanceLevel.INF:
        i_min = DEFAULT_CONFIG.DAC_MAX + 1
    else:
        i_min = LEVEL_TEST_DAC[level.value]

    result = binary_search_range(make_ideal_detect_fn(i_min))

    assert result.level == level
    assert len(result.trace) == DEFAULT_CONFIG.BINARY_SEARCH_DEPTH


def test_exactly_three_transmissions_always():
    for level in DistanceLevel:
        i_min = (
            DEFAULT_CONFIG.DAC_MAX + 1
            if level == DistanceLevel.INF
            else LEVEL_TEST_DAC[level.value]
        )
        result = binary_search_range(make_ideal_detect_fn(i_min))
        assert len(result.trace) == 3