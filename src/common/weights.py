"""Small helpers for survey-weighted statistics."""
import numpy as np


def wsum(values, weights):
    """Weighted total."""
    return float(np.sum(np.asarray(values, float) * np.asarray(weights, float)))


def wshare(mask, weights):
    """Weighted share of rows where mask is True."""
    w = np.asarray(weights, float)
    m = np.asarray(mask, bool)
    return float(w[m].sum() / w.sum())


def wquantile(values, weights, q):
    """Weighted quantile (q between 0 and 1)."""
    v = np.asarray(values, float)
    w = np.asarray(weights, float)
    order = np.argsort(v)
    v, w = v[order], w[order]
    position = (np.cumsum(w) - 0.5 * w) / w.sum()
    return float(np.interp(q, position, v))


def select_weighted(weights, n_target):
    """Weights of the first rows (in current order) that add up to n_target households."""
    w = np.asarray(weights, float)
    before = np.cumsum(w) - w
    return np.clip(n_target - before, 0.0, w)
