"""Run every Project A analysis and save tables and figures."""
import argparse

import numpy as np
import pandas as pd

from ..common import plotting
from ..common.config import ROOT, load_config
from ..common.pipeline import build
from . import affordability, counterfactual, indigent, price_multiplier, revenue, sizing, split


def main(mode=None):
    cfg = load_config()
    mode = mode or cfg["data_mode"]
    base = ROOT / "projects" / "a_who_pays" / "outputs"
    if mode == "synthetic":
        base = base / "synthetic"          # fake results are kept apart and git-ignored
    tables, figures = base / "tables", base / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)

    ghs, ies, nfcm = build(mode)
    th = cfg["thresholds"]

    # 01 non-payment measures (hand-entered, sourced table)
    measures_path = ROOT / "data" / "processed" / "nonpayment_measures.csv"
    if measures_path.exists():
        measures = sizing.load_measures(measures_path)
        latest = sizing.latest_by_measure(measures)
        latest.to_csv(tables / "nonpayment_latest.csv", index=False)

    # 02 affordability
    grid_values = np.arange(th["grid_min"], th["grid_max"] + 1e-9, th["grid_step"])
    grid = affordability.threshold_table(ies, grid_values)
    grid.to_csv(tables / "threshold_grid.csv", index=False)
    by_province = affordability.threshold_table(ies, th["bill_to_income"], by="province")
    by_province.to_csv(tables / "threshold_by_province.csv", index=False)
    plotting.threshold_curve(grid, th["headline"], figures / "threshold_curve.png")

    # 03 indigent registrations
    cutoffs = cfg["indigent"]["income_cutoffs_rand"]
    cov = indigent.coverage_table(ies, nfcm, cutoffs)
    cov.to_csv(tables / "indigent_coverage.csv", index=False)
    headline_cutoff = cfg["indigent"]["headline_cutoff_rand"]
    plotting.coverage_bars(cov, headline_cutoff, figures / "indigent_coverage.png")

    # 04 can't pay versus won't pay
    nonpayers = split.nonpayers_by_province(ghs)
    summaries = []
    for t in th["bill_to_income"]:
        bounds = split.unable_bounds(ies, nonpayers, t)
        summaries.append(split.split_summary(bounds, t))
    summary = pd.DataFrame(summaries)
    summary.to_csv(tables / "split_summary.csv", index=False)
    plotting.split_ranges(summary, figures / "split_ranges.png")

    # 05 counterfactual tariff
    cf = counterfactual.scenario_grid(cfg)
    cf.to_csv(tables / "counterfactual_grid.csv", index=False)
    plotting.counterfactual_bars(cf, figures / "counterfactual.png")

    # 06 revenue from able-to-pay non-payers
    rev = revenue.revenue_table(ies, ghs, cfg)
    rev.to_csv(tables / "revenue_scenarios.csv", index=False)
    revenue.bounds_table(ies, ghs, cfg).to_csv(tables / "revenue_bounds.csv", index=False)
    plotting.revenue_range(rev, th["headline"], figures / "revenue_range.png")

    # 07 real price at which most households face an unaffordable bill
    pm = cfg["price_multiplier"]
    pool = affordability.paying_households(ies)
    mult = price_multiplier.multiplier_table(pool, pm["multipliers"], [0.08, 0.10, 0.12, 0.15])
    mult.to_csv(tables / "price_multiplier_table.csv", index=False)
    crossing = price_multiplier.crossing_table(pool, [0.08, 0.10, 0.12, 0.15], pm["elasticities"])
    crossing.to_csv(tables / "half_crossing_multiplier.csv", index=False)
    years = price_multiplier.years_table(crossing, pm["current_real_multiplier"],
                                         pm["real_growth_rates"])
    years.to_csv(tables / "years_to_crossing.csv", index=False)
    plotting.multiplier_curve(mult, int(round(th["headline"] * 100)), figures / "price_multiplier.png")

    print(f"Done ({mode}). Outputs in {base}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["raw", "synthetic"], default=None)
    main(parser.parse_args().mode)
