"""Turn the three downloaded Stats SA sources into the tables the pipeline reads.

Run once after downloading (from the repository root):
    python -m src.common.prepare_inputs

Inputs  (put in data/raw/statssa/):
    ghs-2025-household-v1.dta            GHS 2025 household file
    ies-2022-2023-total-v1.2.dta         IES 2022/23 household-by-item file
    P9115 time series by province .xlsx  Stats SA NFCM time series
Outputs (written to data/raw/statssa/, git-ignored):
    ies_households.csv   one row per household: province, weight, income, electricity_spend
    nfcm_provincial.csv  one row per province: indigent and free basic electricity households
"""
from pathlib import Path

import numpy as np
import pandas as pd

from .config import ROOT
from .synthetic import PROVINCES

RAW = ROOT / "data" / "raw" / "statssa"

# IES COICOP codes (see the IES COICOP codelist workbook)
ELECTRICITY_BILL = 4510100       # electricity from all sources, incl. standing charges
ELECTRICITY_BUNDLED = 4510300    # combined water, sanitation and electricity bill
FREE_ELECTRICITY = 4510200       # free electricity (in-kind consumption)
CASH_INCOME = 3                  # COICOP type 3
INKIND_INCOME = 4                # COICOP type 4


def _find(pattern):
    hits = sorted(RAW.glob(pattern))
    if not hits:
        raise FileNotFoundError(f"No file matching {pattern} in {RAW}")
    return hits[0]


def prepare_ies(path=None):
    """Household income and electricity spending (annual rand) from the IES item file."""
    path = path or _find("ies-2022-2023-total-v1*.dta")
    items = pd.read_stata(path, convert_categoricals=False)
    items = items.rename(columns={"valueannualized_adj": "value",
                                  "valueannualized_adj_wgt": "value_w"})
    items["weight"] = np.where(items["value"] > 0, items["value_w"] / items["value"], np.nan)
    hh = items.groupby("UQNO")["weight"].max().to_frame()

    def total(mask, name):
        return items[mask].groupby("UQNO")["value"].sum().rename(name)

    parts = [total(items["coicoptype"] == CASH_INCOME, "income_cash"),
             total(items["coicoptype"] == INKIND_INCOME, "income_inkind"),
             total(items["coicop"] == ELECTRICITY_BILL, "electricity_spend"),
             total(items["coicop"] == ELECTRICITY_BUNDLED, "electricity_bundled"),
             total(items["coicop"] == FREE_ELECTRICITY, "free_electricity_value")]
    hh = pd.concat([hh] + parts, axis=1).fillna(0.0)
    hh["income"] = hh["income_cash"] + hh["income_inkind"]
    # ASSUMPTION to verify: the first digit of the household identifier is the province code
    hh["province"] = hh.index.str[0].astype(int)
    hh = hh.reset_index()
    out = RAW / "ies_households.csv"
    hh.to_csv(out, index=False)
    return hh


def prepare_nfcm(year="2023*", path=None):
    """Provincial indigent households and free basic electricity households."""
    path = path or _find("P9115*.xlsx")
    sheet = pd.read_excel(path, header=0)
    sheet.columns = [str(c) for c in sheet.columns]
    if year not in sheet.columns:
        raise KeyError(f"Year column {year!r} not found. Columns: {list(sheet.columns)[13:]}")
    prov = sheet["H13"].astype(str).str.strip()
    indigent = sheet[(sheet["H08"] == "Indigent households identified by the municipalities")]
    fbe = sheet[(sheet["H08"] == "Free Basic Electricity")]
    table = pd.DataFrame({
        "province": indigent["H13"].astype(str).str.strip().values,
        "indigent_households": indigent[year].values,
    }).merge(pd.DataFrame({"province": fbe["H13"].astype(str).str.strip().values,
                           "fbe_households": fbe[year].values}), on="province")
    table = table[table["province"].isin(PROVINCES)]
    table.to_csv(RAW / "nfcm_provincial.csv", index=False)
    return table


if __name__ == "__main__":
    ies = prepare_ies()
    print(f"IES: {len(ies):,} households, weighted {ies['weight'].sum() / 1e6:.2f} million")
    nfcm = prepare_nfcm()
    print(nfcm.to_string(index=False))
