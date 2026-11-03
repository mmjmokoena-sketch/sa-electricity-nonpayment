"""Step A9: how stable are the headline results?

Run from the project folder:
    python -m src.a_who_pays.robustness
Each row changes ONE thing and shows how far the answer moves.
"""
import numpy as np
import pandas as pd

from ..common.config import ROOT, load_config
from ..common.pipeline import build
from . import affordability, revenue, split


def share_above(pool, threshold, weighted=True):
    """Share of households with a bill at or above the threshold."""
    above = (pool["bill_share"] >= threshold).values
    w = pool["weight"].values if weighted else np.ones(len(pool))
    return float(w[above].sum() / w.sum())


def smallest_provinces(ies, n=2):
    """The n provinces with the fewest weighted households."""
    totals = ies.groupby("province")["weight"].sum().sort_values()
    return list(totals.index[:n])


def mid_able_share(ies, ghs, threshold):
    nonpayers = split.nonpayers_by_province(ghs)
    return split.split_summary(split.unable_bounds(ies, nonpayers, threshold), threshold)["able_share_mid"]


def run_checks(ies, ghs, cfg, ies_extra=None):
    """Return a table of baseline against alternative for each check."""
    t = cfg["thresholds"]["headline"]
    pool = affordability.paying_households(ies)
    rows = []

    def add(name, baseline, alternative, unit="share"):
        rows.append({"check": name, "baseline": baseline, "alternative": alternative,
                     "difference": alternative - baseline, "unit": unit})

    base = share_above(pool, t)
    add("Households above the line: unweighted instead of weighted", base,
        share_above(pool, t, weighted=False))

    drop = smallest_provinces(ies, 2)
    pool_drop = pool[~pool["province"].isin(drop)]
    add(f"Households above the line: without {drop[0]} and {drop[1]}", base, share_above(pool_drop, t))

    if ies_extra is not None and "income_cash" in ies_extra.columns:
        extra = ies_extra.copy()
        extra["income"] = extra["income_cash"] / cfg["units"]["ies_income_divisor"]
        extra["electricity_spend"] = extra["electricity_spend"] / cfg["units"]["ies_income_divisor"]
        extra = extra[(extra["income"] > 0)]
        pool_cash = affordability.paying_households(extra[["province", "weight", "income", "electricity_spend"]])
        add("Households above the line: cash income only (no in-kind)", base, share_above(pool_cash, t))
        if "free_electricity_value" in extra.columns:
            no_free = extra[extra["free_electricity_value"] <= 0]
            pool_nf = affordability.paying_households(no_free[["province", "weight", "income", "electricity_spend"]])
            add("Households above the line: excluding households with free electricity", base,
                share_above(pool_nf, t))

    add("Able-to-pay share (middle case): without the two smallest provinces",
        mid_able_share(ies, ghs, t),
        mid_able_share(ies[~ies["province"].isin(drop)], ghs[~ghs["province"].isin(drop)], t))

    table = revenue.revenue_table(ies, ghs, cfg)
    one = table[(table["threshold"] == t) & (table["pool_share"] == 0.5) & (table["collection_rate"] == 1.0)].iloc[0]
    add("Revenue (R bn, poorest 50% pool): price factor low instead of central",
        one["revenue_rbn_central"], one["revenue_rbn_low"], unit="R bn")
    add("Revenue (R bn, poorest 50% pool): price factor high instead of central",
        one["revenue_rbn_central"], one["revenue_rbn_high"], unit="R bn")
    return pd.DataFrame(rows)


def main():
    cfg = load_config()
    ghs, ies, _ = build()
    extra_path = ROOT / "data" / "raw" / "statssa" / "ies_households.csv"
    extra = pd.read_csv(extra_path) if extra_path.exists() else None
    if extra is not None:
        extra["province"] = extra["province"].map(
            {1: "Western Cape", 2: "Eastern Cape", 3: "Northern Cape", 4: "Free State",
             5: "KwaZulu-Natal", 6: "North West", 7: "Gauteng", 8: "Mpumalanga", 9: "Limpopo"})
    table = run_checks(ies, ghs, cfg, extra)
    shown = table.copy()
    for col in ("baseline", "alternative", "difference"):
        shown[col] = [f"{v:.1%}" if u == "share" else f"{v:.2f}" for v, u in zip(table[col], table["unit"])]
    print(shown[["check", "baseline", "alternative", "difference"]].to_string(index=False))
    out = ROOT / "projects" / "a_who_pays" / "outputs" / "tables" / "robustness.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(out, index=False)
    print(f"\nSaved {out}")


if __name__ == "__main__":
    main()
