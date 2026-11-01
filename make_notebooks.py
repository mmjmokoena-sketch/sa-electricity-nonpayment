"""Generate the five Project A notebooks (run once: python make_notebooks.py)."""
from pathlib import Path

import nbformat as nbf

OUT = Path("projects/a_who_pays/notebooks")
OUT.mkdir(parents=True, exist_ok=True)

SETUP = '''import os
import sys
from pathlib import Path

ROOT = Path.cwd().resolve().parents[2]      # repo root, two levels above this folder
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import pandas as pd

from src.common.config import load_config
from src.common.pipeline import build

cfg = load_config()
MODE = os.environ.get("DATA_MODE")          # None = use config; "synthetic" = fake
ghs, ies, nfcm = build(MODE, save=False)'''


def make(name, title, intro, cells):
    nb = nbf.v4.new_notebook()
    nb.cells = [nbf.v4.new_markdown_cell(f"# {title}\n\n{intro}"),
                nbf.v4.new_code_cell(SETUP)]
    for kind, text in cells:
        nb.cells.append(nbf.v4.new_markdown_cell(text) if kind == "md" else nbf.v4.new_code_cell(text))
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nbf.write(nb, OUT / name)


make("01_non_payment_sizing.ipynb", "01 Sizing non-payment",
     "Put the different non-payment measures side by side. They measure different things, so do not force them into one number.",
     [("code", '''from src.a_who_pays import sizing

measures = sizing.load_measures(ROOT / "data" / "processed" / "nonpayment_measures.csv")
measures'''),
      ("md", "Anything with `verified = False` must be checked against a primary source before it is used in the paper."),
      ("code", '''latest = sizing.latest_by_measure(measures)
latest'''),
      ("code", '''growth = sizing.annual_growth(measures, "municipal_debt_to_eskom")
print(f"Municipal debt to Eskom, compound annual growth: {growth:.1%}")'''),
      ("code", '''debt = measures[measures["measure"] == "municipal_debt_to_eskom"]
plt.plot(debt["date"], debt["value"], marker="o")
plt.ylabel("Rand billion")
plt.title("Municipal debt to Eskom")
plt.show()''')])

make("02_statssa_affordability.ipynb", "02 Affordability",
     "How many households would find their electricity bill unaffordable at each threshold?",
     [("code", '''from src.a_who_pays import affordability

th = cfg["thresholds"]
affordability.threshold_table(ies, th["bill_to_income"])'''),
      ("md", "Check the pattern behind the bounds method in notebook 04: the average bill share should fall as income rises."),
      ("code", '''affordability.bill_share_by_decile(ies)'''),
      ("code", '''by_province = affordability.threshold_table(ies, [th["headline"]], by="province")
by_province.sort_values("share_above", ascending=False)'''),
      ("code", '''import numpy as np

grid_values = np.arange(th["grid_min"], th["grid_max"] + 1e-9, th["grid_step"])
grid = affordability.threshold_table(ies, grid_values)
plt.plot(grid["threshold"] * 100, grid["share_above"] * 100, marker="o")
plt.xlabel("Threshold (% of income)")
plt.ylabel("Households above (%)")
plt.show()''')])

make("03_indigent_registrations.ipynb", "03 Indigent registrations",
     "Compare registered indigent households with households that qualify on income.",
     [("code", '''from src.a_who_pays import indigent

cutoffs = cfg["indigent"]["income_cutoffs_rand"]
cov = indigent.coverage_table(ies, nfcm, cutoffs)
cov'''),
      ("md", "Coverage above 100% means more households are registered than qualify on the income cut-off used. Municipal cut-offs differ, so compare several."),
      ("code", '''cut = cfg["indigent"]["headline_cutoff_rand"]
headline = cov[cov["cutoff_rand"] == cut].sort_values("coverage")
headline.plot.barh(x="province", y="coverage", legend=False)
plt.xlabel("Registered / qualifying households")
plt.show()''')])

make("04_cant_vs_wont_split.ipynb", "04 Can't pay versus won't pay",
     "Bound the number of non-paying households that could afford to pay, using three assumptions about who the non-payers are.",
     [("code", '''from src.a_who_pays import split

nonpayers = split.nonpayers_by_province(ghs)
nonpayers'''),
      ("code", '''rows = []
for t in cfg["thresholds"]["bill_to_income"]:
    bounds = split.unable_bounds(ies, nonpayers, t)
    rows.append(split.split_summary(bounds, t))
summary = pd.DataFrame(rows)
summary'''),
      ("md", "Report the low-to-high range. The mid case assumes non-payers look like all households with a bill."),
      ("code", '''labels = [f"{t * 100:.0f}% threshold" for t in summary["threshold"]]
mid = summary["able_share_mid"] * 100
low = mid - summary["able_share_low"] * 100
high = summary["able_share_high"] * 100 - mid
plt.errorbar(mid, labels, xerr=[low, high], fmt="o", capsize=5)
plt.xlabel("Non-paying households able to pay (%)")
plt.show()''')])

make("05_counterfactual_tariff.ipynb", "05 Counterfactual tariff",
     "What would payers be charged if able-to-pay non-payers paid? A stylised full-recovery measure, not the legal tariff.",
     [("md", "**Baby-steps check.** Costs R100, 90 units paid, 10 unpaid, half of the unpaid can afford to pay."),
      ("code", '''from src.a_who_pays import counterfactual as cf

t = cf.payers_only_tariff(100, 90)
t_new = cf.counterfactual_tariff(100, 90, 10, 0.5)
change = cf.pct_change(t, t_new)
print(round(t, 4), round(t_new, 4), round(change, 2))     # 1.1111 1.0526 -5.26'''),
      ("md", "**Practice question.** Costs R200, 160 paid, 40 unpaid, a quarter of the unpaid can afford to pay. Fill in the numbers and check your answer."),
      ("code", '''# t = ?   t_new = ?   change = ?   (answer: 1.25, 1.1765, -5.88%)'''),
      ("code", '''grid = cf.scenario_grid(cfg)
grid.round(2)'''),
      ("code", '''for u, g in grid.groupby("unpaid_share"):
    plt.plot(g["able_share"] * 100, g["change_vs_payers_only_pct"],
             marker="o", label=f"unpaid {u:.1%}")
plt.xlabel("Share of non-payers able to pay (%)")
plt.ylabel("Change in price for payers (%)")
plt.legend()
plt.show()''')])
make("06_revenue_scenarios.ipynb", "06 Revenue from able-to-pay non-payers",
     "How much could households that can afford a bill but do not pay add each year? Scenarios, not forecasts.",
     [("md", "**Baby-steps check.** 1.8 million able households at an average bill of R3,264 a year gives R5.9 billion at survey prices. Multiply by the 1.34 price factor to move from 2022/23 to 2025/26 prices: about R7.9 billion."),
      ("code", '''print(round(1.8e6 * 3264 / 1e9, 2), round(1.8e6 * 3264 * 1.34 / 1e9, 2))   # 5.88 7.88'''),
      ("code", '''from src.a_who_pays import revenue

rev = revenue.revenue_table(ies, ghs, cfg)
headline = rev[(rev["threshold"] == cfg["thresholds"]["headline"]) & (rev["collection_rate"] == 1.0)]
headline[["pool_share", "able_households_m", "avg_bill_rand_survey", "revenue_rbn_low",
          "revenue_rbn_central", "revenue_rbn_high", "eskom_direct_rbn_central",
          "pct_of_allowable_revenue"]].round(2)'''),
      ("md", "**Question.** The pool share is who the non-payers are assumed to resemble. Which rows do you think are realistic, and why is the last row probably too high?"),
      ("code", '''one = rev[(rev["threshold"] == cfg["thresholds"]["headline"]) & (rev["pool_share"] == 0.5)]
one[["collection_rate", "paying_households_m", "revenue_rbn_central", "eskom_direct_rbn_central"]].round(2)'''),
      ("code", '''revenue.bounds_table(ies, ghs, cfg).round(2)'''),
      ("code", '''revenue.supplier_shares(ghs)   # who supplies the non-paying households''')])

make("07_price_multiplier.ipynb", "07 The real price at which most households are priced out",
     "How much would the real price have to rise before most households with a bill spend over the affordability line?",
     [("md", "**Baby-steps check.** Two households: bills of 5% and 3% of income. The price doubles, so the bills become 10% and 6%. At a 10% line only the first is above it, so half of the households are."),
      ("code", '''from src.a_who_pays import affordability, price_multiplier as pm

pool = affordability.paying_households(ies)
mult = pm.multiplier_table(pool, cfg["price_multiplier"]["multipliers"], [0.08, 0.10, 0.12, 0.15])
mult.round(3)'''),
      ("code", '''crossing = pm.crossing_table(pool, [0.08, 0.10, 0.12, 0.15], cfg["price_multiplier"]["elasticities"])
crossing.round(2)'''),
      ("md", "**Question.** What does elasticity -0.5 do to the real price needed, and why is a household cutting its use not good news?"),
      ("code", '''cfg_pm = cfg["price_multiplier"]
pm.years_table(crossing, cfg_pm["current_real_multiplier"], cfg_pm["real_growth_rates"]).round(1)'''),
      ("code", '''print(round(pm.years_to_reach(2.0, 1.0, 0.07), 2))   # years to double at 7% a year: 10.24''')])
print("notebooks written")
