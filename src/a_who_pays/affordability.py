"""Notebook 02: how many households would find their electricity bill unaffordable?"""
import numpy as np
import pandas as pd

from ..common.weights import wquantile


def add_bill_share(ies):
    """Add bill_share = electricity spend / income, for households that have a bill."""
    df = ies.copy()
    df["has_bill"] = df["electricity_spend"] > 0
    ratio = df["electricity_spend"] / df["income"]
    df["bill_share"] = np.where(df["has_bill"], ratio, np.nan)
    return df


def add_income_decile(ies):
    """Weighted income deciles 1 (poorest) to 10 (richest)."""
    df = ies.copy()
    edges = [wquantile(df["income"], df["weight"], q) for q in np.linspace(0.1, 0.9, 9)]
    df["decile"] = np.digitize(df["income"], edges) + 1
    return df


def threshold_table(ies, thresholds, by=None):
    """Households (and share) whose bill share is at or above each threshold."""
    df = add_bill_share(ies)
    df = df[df["has_bill"]]
    groups = [("All", df)] if by is None else list(df.groupby(by))
    rows = []
    for label, g in groups:
        total = float(g["weight"].sum())
        for t in thresholds:
            above = float(g.loc[g["bill_share"] >= t, "weight"].sum())
            rows.append({"group": label, "threshold": round(float(t), 4),
                         "households_above": above, "share_above": above / total,
                         "households_with_bill": total})
    return pd.DataFrame(rows)


def bill_share_by_decile(ies):
    """Average bill share by income decile (should be higher for poorer households)."""
    df = add_income_decile(add_bill_share(ies))
    df = df[df["has_bill"]]
    rows = []
    for decile, g in df.groupby("decile"):
        rows.append({
            "decile": int(decile),
            "median_income": wquantile(g["income"], g["weight"], 0.5),
            "mean_bill_share": float(
                (g["bill_share"] * g["weight"]).sum() / g["weight"].sum()),
        })
    return pd.DataFrame(rows)


def paying_households(ies):
    """Households with an electricity bill, with bill share and annual bill in rand.

    Amounts in the cleaned IES are monthly, so the annual bill is twelve times the monthly one.
    """
    df = add_bill_share(ies)
    df = df[df["has_bill"]].copy()
    df["bill_year"] = df["electricity_spend"] * 12
    return df
