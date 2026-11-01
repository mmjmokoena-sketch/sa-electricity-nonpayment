"""Notebook 07: at what real price do most households face an unaffordable bill?

The real price multiplier m is how much more electricity costs relative to household income
than in the survey year. With demand elasticity e, a bill changes by m ** (1 + e): price goes
up by m, quantity changes by m ** e. Elasticity 0 means households keep using the same amount.
"""
import numpy as np
import pandas as pd


def share_above(pool, m, threshold, elasticity=0.0):
    """Weighted share of paying households whose bill is at or above the threshold."""
    bill_multiplier = m ** (1 + elasticity)
    above = pool["bill_share"].values * bill_multiplier >= threshold
    return float(pool["weight"].values[above].sum() / pool["weight"].sum())


def multiplier_table(pool, multipliers, thresholds, elasticity=0.0):
    rows = []
    for m in multipliers:
        row = {"multiplier": m}
        for t in thresholds:
            row[f"share_above_{int(round(t * 100))}pct"] = share_above(pool, m, t, elasticity)
        rows.append(row)
    return pd.DataFrame(rows)


def crossing_multiplier(pool, threshold, elasticity=0.0, target=0.5, upper=200.0):
    """Smallest real price multiplier at which `target` of households reach the threshold."""
    low, high = 1.0, upper
    if share_above(pool, high, threshold, elasticity) < target:
        return np.nan
    for _ in range(80):
        mid = (low + high) / 2
        if share_above(pool, mid, threshold, elasticity) >= target:
            high = mid
        else:
            low = mid
    return high


def crossing_table(pool, thresholds, elasticities, target=0.5):
    rows = []
    for t in thresholds:
        row = {"threshold": t}
        for e in elasticities:
            row[f"elasticity_{e}"] = crossing_multiplier(pool, t, e, target)
        rows.append(row)
    return pd.DataFrame(rows)


def years_to_reach(target_multiplier, current_multiplier, real_growth):
    """Years of steady real price growth needed to move from current to target."""
    return float(np.log(target_multiplier / current_multiplier) / np.log(1 + real_growth))


def years_table(crossing, current_multiplier, growth_rates, elasticity=0.0):
    col = f"elasticity_{elasticity}"
    rows = []
    for _, r in crossing.iterrows():
        row = {"threshold": r["threshold"], "multiplier_needed": r[col]}
        for g in growth_rates:
            row[f"years_at_{int(round(g * 100))}pct"] = years_to_reach(r[col], current_multiplier, g)
        rows.append(row)
    return pd.DataFrame(rows)
