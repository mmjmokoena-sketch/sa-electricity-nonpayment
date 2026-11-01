import numpy as np

from src.common.weights import select_weighted, wquantile, wshare


def test_select_weighted_takes_partial_last_row():
    assert list(select_weighted([10, 10, 10], 15)) == [10, 5, 0]


def test_select_weighted_never_exceeds_target():
    chosen = select_weighted([3, 4, 5, 6], 9)
    assert abs(chosen.sum() - 9) < 1e-9


def test_wshare_uses_weights():
    mask = np.array([True, False])
    assert abs(wshare(mask, [3, 1]) - 0.75) < 1e-9


def test_wquantile_median_of_equal_weights():
    assert abs(wquantile([1, 2, 3], [1, 1, 1], 0.5) - 2) < 1e-9
