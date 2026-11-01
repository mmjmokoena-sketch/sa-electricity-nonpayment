"""Notebook 04: can't pay versus won't pay, using bounds instead of one guessed number.

Two surveys cannot be linked household by household, so we bound the answer. For each
province we take the number of non-paying households (household survey) and ask what share
of them would find the bill unaffordable (income survey) under three assumptions about
WHO the non-payers are:
  poorest-first : non-payers are the poorest households (most "unable")
  random        : non-payers look like all households with a bill
  richest-first : non-payers are the richest households (fewest "unable")
Poorest-first being the most "unable" assumes bill shares fall as income rises; check this
in the data before relying on it.
"""
import pandas as pd

from ..common.weights import select_weighted, wshare
from .affordability import add_bill_share


def nonpayers_by_province(ghs):
    """Weighted number of electricity-using households that say they do not pay."""
    no = ghs[ghs["pays_electricity"] == "no"]
    return no.groupby("province")["weight"].sum()


def unable_bounds(ies, nonpayers, threshold):
    df = add_bill_share(ies)
    df = df[df["has_bill"]].copy()
    df["unable"] = (df["bill_share"] >= threshold).astype(float)
    rows = []
    for province, g in df.groupby("province"):
        n = min(float(nonpayers.get(province, 0.0)), float(g["weight"].sum()))
        if n <= 0:
            continue
        poorest = g.sort_values("income", ascending=True)
        richest = g.sort_values("income", ascending=False)
        w_poor = select_weighted(poorest["weight"].values, n)
        w_rich = select_weighted(richest["weight"].values, n)
        rows.append({
            "province": province,
            "nonpayers": n,
            "unable_poorest_first": float((w_poor * poorest["unable"].values).sum()),
            "unable_random": float(n * wshare(g["unable"].values > 0, g["weight"].values)),
            "unable_richest_first": float((w_rich * richest["unable"].values).sum()),
        })
    return pd.DataFrame(rows)


def split_summary(bounds, threshold):
    """National totals: how many non-paying households could afford to pay."""
    n = bounds["nonpayers"].sum()
    able_low = n - bounds["unable_poorest_first"].sum()
    able_mid = n - bounds["unable_random"].sum()
    able_high = n - bounds["unable_richest_first"].sum()
    return {"threshold": threshold, "nonpaying_households": n,
            "able_to_pay_low": able_low, "able_to_pay_mid": able_mid,
            "able_to_pay_high": able_high,
            "able_share_low": able_low / n, "able_share_mid": able_mid / n,
            "able_share_high": able_high / n}
