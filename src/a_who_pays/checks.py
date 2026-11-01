"""Step A2: reconcile your data with published totals before you trust any result.

Run from the project folder (after prepare_inputs):
    python -m src.a_who_pays.checks
Each line says PASS, or CHECK when something should be looked at.
"""
import numpy as np
import pandas as pd

from ..common.config import ROOT, load_config
from ..common.pipeline import read_table
from ..common.weights import wquantile

# Published by Stats SA: GHS 2025 statistical release (P0318), Table 2.2, thousands of households
GHS_PUBLISHED = {1: 2256, 2: 1799, 3: 397, 4: 1049, 5: 3483, 6: 1476, 7: 6193, 8: 1591, 9: 1870}
GHS_PUBLISHED_TOTAL = 20114
# Published by Stats SA: IES 2022/23 median annual household income (2023 rand)
IES_PUBLISHED_MEDIAN = 95770
# Stats SA NFCM time series, 2023*, national totals
NFCM_INDIGENT_TOTAL = 2757643
NFCM_FBE_TOTAL = 1849746
PROVINCES = {1: "Western Cape", 2: "Eastern Cape", 3: "Northern Cape", 4: "Free State",
             5: "KwaZulu-Natal", 6: "North West", 7: "Gauteng", 8: "Mpumalanga", 9: "Limpopo"}


def report(name, ok, detail):
    print(f"{'PASS ' if ok else 'CHECK'} | {name}: {detail}")
    return ok


def main():
    cfg = load_config()
    cm = cfg["column_map"]
    results = []

    # 1. GHS weights against the published household totals
    ghs = read_table(cfg["paths"]["ghs"])
    w, prov = ghs[cm["ghs"]["weight"]], ghs[cm["ghs"]["province"]]
    total = w.sum() / 1000
    results.append(report("GHS household total", abs(total / GHS_PUBLISHED_TOTAL - 1) < 0.001,
                          f"{total:,.0f} thousand vs published {GHS_PUBLISHED_TOTAL:,}"))
    by_prov = (w.groupby(prov).sum() / 1000).round(0)
    worst = max(abs(by_prov[k] / v - 1) for k, v in GHS_PUBLISHED.items())
    results.append(report("GHS provincial totals", worst < 0.002,
                          f"largest gap to the published table is {worst:.2%}"))

    # 2. How many households say they do not pay
    pay = ghs[cm["ghs"]["pays_electricity"]]
    no = w[pay == 2].sum()
    yes = w[pay == 1].sum()
    results.append(report("Non-paying households (GHS)", 2.0e6 < no < 3.5e6,
                          f"{no / 1e6:.2f} million, {no / (no + yes):.1%} of those answering yes or no"))

    # 3. IES household table
    ies = pd.read_csv(ROOT / "data" / "raw" / "statssa" / "ies_households.csv")
    ies_total = ies["weight"].sum() / 1e6
    results.append(report("IES weighted households", 19 < ies_total < 23,
                          f"{ies_total:.2f} million (GHS 2025 says {total / 1000:.2f} million)"))
    has_bill = ies.loc[ies["electricity_spend"] > 0, "weight"].sum() / ies["weight"].sum()
    ghs_yes = yes / w.sum()
    results.append(report("Share with an electricity bill: IES vs GHS", abs(has_bill - ghs_yes) < 0.03,
                          f"IES {has_bill:.1%}, GHS says they pay {ghs_yes:.1%}"))
    median = wquantile(ies["income"], ies["weight"], 0.5)
    results.append(report("IES median annual income", abs(median / IES_PUBLISHED_MEDIAN - 1) < 0.03,
                          f"R{median:,.0f} vs published R{IES_PUBLISHED_MEDIAN:,}"))

    # 4. The province assumption: do medians look plausible?
    print("\nProvince check (IES): weighted median annual household income and household share.")
    print("Western Cape and Gauteng should be near the top; Eastern Cape and Limpopo near the bottom.")
    rows = []
    for code, g in ies.groupby("province"):
        rows.append({"province": PROVINCES[code],
                     "median_income": round(wquantile(g["income"], g["weight"], 0.5)),
                     "share_of_households_%": round(g["weight"].sum() / ies["weight"].sum() * 100, 1),
                     "GHS_share_%": round(by_prov[code] / total * 100, 1)})
    print(pd.DataFrame(rows).sort_values("median_income", ascending=False).to_string(index=False))

    # 5. NFCM totals
    nfcm = pd.read_csv(ROOT / "data" / "raw" / "statssa" / "nfcm_provincial.csv")
    results.append(report("NFCM indigent households", nfcm["indigent_households"].sum() == NFCM_INDIGENT_TOTAL,
                          f"{nfcm['indigent_households'].sum():,} vs published total {NFCM_INDIGENT_TOTAL:,}"))
    results.append(report("NFCM free basic electricity", nfcm["fbe_households"].sum() == NFCM_FBE_TOTAL,
                          f"{nfcm['fbe_households'].sum():,} vs published total {NFCM_FBE_TOTAL:,}"))

    print(f"\n{sum(results)} of {len(results)} checks passed.")


if __name__ == "__main__":
    main()
