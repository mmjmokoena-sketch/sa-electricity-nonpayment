"""Notebook 06: how much revenue could able-to-pay non-payers add?

Idea: take the number of non-paying households in each province (household survey), assume
they look like a chosen slice of the paying households (income survey), keep those who can
afford a bill (bill below the threshold) and add up the bills those households pay.
"""
import numpy as np
import pandas as pd

from ..common.weights import select_weighted
from .affordability import paying_households
from .split import nonpayers_by_province


def revenue_for_pool(pool, nonpayers, threshold, pool_share):
    """Able households and revenue (rand a year, survey prices) if non-payers are a random
    draw from the poorest `pool_share` of paying households in each province."""
    pool = pool.copy()
    pool["able"] = (pool["bill_share"] < threshold).astype(float)
    able_households, revenue = 0.0, 0.0
    for province, g in pool.groupby("province"):
        n = min(float(nonpayers.get(province, 0.0)), float(g["weight"].sum()))
        if n <= 0:
            continue
        g = g.sort_values("income")
        w = select_weighted(g["weight"].values, pool_share * g["weight"].sum())
        able_w = w * g["able"].values
        if w.sum() <= 0 or able_w.sum() <= 0:
            continue
        share_able = able_w.sum() / w.sum()
        mean_bill = (able_w * g["bill_year"].values).sum() / able_w.sum()
        able_households += n * share_able
        revenue += n * share_able * mean_bill
    return able_households, revenue


def revenue_bounds(pool, nonpayers, threshold):
    """Extreme cases: non-payers are the poorest paying households, or the richest."""
    pool = pool.copy()
    pool["able"] = (pool["bill_share"] < threshold).astype(float)
    out = {}
    for name, ascending in (("poorest_first", True), ("richest_first", False)):
        able_households, revenue = 0.0, 0.0
        for province, g in pool.groupby("province"):
            n = min(float(nonpayers.get(province, 0.0)), float(g["weight"].sum()))
            if n <= 0:
                continue
            g = g.sort_values("income", ascending=ascending)
            w = select_weighted(g["weight"].values, n)
            able_households += float((w * g["able"].values).sum())
            revenue += float((w * g["able"].values * g["bill_year"].values).sum())
        out[name] = (able_households, revenue)
    return out


def supplier_shares(ghs):
    """Share of non-paying households supplied by Eskom, by a municipality, or other."""
    if "supplier" not in ghs.columns:
        return {}
    no = ghs[ghs["pays_electricity"] == "no"]
    w = no.groupby("supplier")["weight"].sum()
    return (w / w.sum()).to_dict()


def revenue_table(ies, ghs, cfg):
    """Every combination of threshold, non-payer pool and collection rate."""
    pool = paying_households(ies)
    nonpayers = nonpayers_by_province(ghs)
    shares = supplier_shares(ghs)
    eskom_share = shares.get("eskom", np.nan)
    factors = cfg["price_update"]
    tariff = cfg["tariff"]
    allowable = tariff["allowable_revenue_rand_bn"]
    kwh = tariff["sales_volume_gwh"] * 1e6
    rows = []
    for threshold in cfg["thresholds"]["bill_to_income"]:
        for pool_share in cfg["scenarios"]["nonpayer_pool_share"]:
            able, rev = revenue_for_pool(pool, nonpayers, threshold, pool_share)
            for rate in cfg["scenarios"]["collection_rate"]:
                central = rev * factors["factor_central"] * rate / 1e9
                rows.append({
                    "threshold": threshold, "pool_share": pool_share, "collection_rate": rate,
                    "able_households_m": able / 1e6,
                    "paying_households_m": able * rate / 1e6,
                    "avg_bill_rand_survey": rev / able if able else np.nan,
                    "revenue_rbn_survey_prices": rev * rate / 1e9,
                    "revenue_rbn_low": rev * factors["factor_low"] * rate / 1e9,
                    "revenue_rbn_central": central,
                    "revenue_rbn_high": rev * factors["factor_high"] * rate / 1e9,
                    "eskom_direct_rbn_central": central * eskom_share,
                    "pct_of_allowable_revenue": central / allowable * 100,
                    "cents_per_kwh_equivalent": central * 1e9 / kwh * 100,
                })
    return pd.DataFrame(rows)


def bounds_table(ies, ghs, cfg):
    """Revenue under the two extreme assumptions, at central prices and full collection."""
    pool = paying_households(ies)
    nonpayers = nonpayers_by_province(ghs)
    factor = cfg["price_update"]["factor_central"]
    rows = []
    for threshold in cfg["thresholds"]["bill_to_income"]:
        for name, (able, rev) in revenue_bounds(pool, nonpayers, threshold).items():
            rows.append({"threshold": threshold, "assumption": name,
                         "able_households_m": able / 1e6,
                         "revenue_rbn_central": rev * factor / 1e9})
    return pd.DataFrame(rows)
