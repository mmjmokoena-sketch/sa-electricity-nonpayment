"""Build clean, analysis-ready tables from raw (or synthetic demo) inputs."""
import argparse

import numpy as np
import pandas as pd

from .config import ROOT, load_config
from .synthetic import PROVINCES, make_synthetic

CODES = {1: "Western Cape", 2: "Eastern Cape", 3: "Northern Cape", 4: "Free State",
         5: "KwaZulu-Natal", 6: "North West", 7: "Gauteng", 8: "Mpumalanga", 9: "Limpopo"}
ALIASES = {"wc": "Western Cape", "ec": "Eastern Cape", "nc": "Northern Cape",
           "fs": "Free State", "kzn": "KwaZulu-Natal", "kwazulu natal": "KwaZulu-Natal",
           "nw": "North West", "gp": "Gauteng", "mp": "Mpumalanga", "lp": "Limpopo"}
for _name in PROVINCES:
    ALIASES[_name.lower()] = _name


def read_table(path):
    """Read csv, Stata, SPSS or Excel files, chosen by file extension."""
    full = ROOT / path
    if not full.exists():
        raise FileNotFoundError(f"{full} not found. Download it, update 'paths' in config.")
    suffix = full.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(full, low_memory=False)
    if suffix == ".dta":
        return pd.read_stata(full, convert_categoricals=False)
    if suffix == ".sav":
        return pd.read_spss(full, convert_categoricals=False)
    if suffix in (".xlsx", ".xls"):
        return pd.read_excel(full)
    raise ValueError(f"Unsupported file type: {suffix}")


def _province(value):
    if pd.isna(value):
        return np.nan
    try:
        return CODES[int(value)]
    except (ValueError, TypeError, KeyError):
        return ALIASES.get(str(value).strip().lower(), np.nan)


def normalise_province(series):
    """Turn Stats SA codes (1-9), abbreviations or names into the nine province names."""
    return series.map(_province)


def standardise(df, mapping):
    """Keep only the mapped columns and rename them to our canonical names."""
    missing = [col for col in mapping.values() if col not in df.columns]
    if missing:
        raise KeyError(f"Columns not found: {missing}. Edit column_map in the config.")
    inverse = {raw_name: ours for ours, raw_name in mapping.items()}
    return df[list(inverse)].rename(columns=inverse).copy()


def _pays(value):
    text = str(value).strip().lower()
    if text in ("1", "1.0", "yes"):
        return "yes"
    if text in ("2", "2.0", "no"):
        return "no"
    return np.nan


def _supplier(value):
    try:
        code = int(value)
    except (ValueError, TypeError):
        return np.nan
    return {1: "municipality", 2: "eskom"}.get(code, "other")


def clean_ghs(raw, cfg):
    df = standardise(raw, cfg["column_map"]["ghs"])
    df["province"] = normalise_province(df["province"])
    df["pays_electricity"] = df["pays_electricity"].map(_pays)
    if "supplier" in df.columns:
        df["supplier"] = df["supplier"].map(_supplier)
    df = df.dropna(subset=["province", "weight", "pays_electricity"])
    return df[df["weight"] > 0].reset_index(drop=True)


def clean_ies(raw, cfg):
    df = standardise(raw, cfg["column_map"]["ies"])
    divisor = cfg["units"]["ies_income_divisor"]
    df["province"] = normalise_province(df["province"])
    df["income"] = df["income"] / divisor
    df["electricity_spend"] = df["electricity_spend"].fillna(0).clip(lower=0) / divisor
    df = df.dropna(subset=["province", "weight", "income"])
    return df[(df["weight"] > 0) & (df["income"] > 0)].reset_index(drop=True)


def clean_nfcm(raw, cfg):
    df = standardise(raw, cfg["column_map"]["nfcm"])
    df["province"] = normalise_province(df["province"])
    df = df.dropna(subset=["province"])
    cols = ["indigent_registered", "fbe_households"]
    return df.groupby("province", as_index=False)[cols].sum()


def validate(ghs, ies, nfcm):
    """Fail loudly on the mistakes that quietly ruin results."""
    problems = []
    for name, df in (("GHS", ghs), ("IES", ies), ("NFCM", nfcm)):
        missing = set(PROVINCES) - set(df["province"])
        if missing:
            problems.append(f"{name} is missing provinces: {sorted(missing)}")
    if (ies["electricity_spend"] > ies["income"]).mean() > 0.05:
        problems.append("Over 5% of households spend more than they earn: check units")
    if problems:
        raise ValueError("; ".join(problems))


def build(mode=None, save=True):
    """Return clean (ghs, ies, nfcm); optionally save them to data/interim/<mode>/."""
    cfg = load_config()
    mode = mode or cfg["data_mode"]
    if mode == "synthetic":
        print("WARNING: SYNTHETIC demo data in use. Never publish results built from it.")
        raw = make_synthetic(cfg)
    else:
        raw = {key: read_table(cfg["paths"][key]) for key in ("ghs", "ies", "nfcm")}
    ghs = clean_ghs(raw["ghs"], cfg)
    ies = clean_ies(raw["ies"], cfg)
    nfcm = clean_nfcm(raw["nfcm"], cfg)
    validate(ghs, ies, nfcm)
    if save:
        out = ROOT / "data" / "interim" / mode
        out.mkdir(parents=True, exist_ok=True)
        for name, df in (("ghs", ghs), ("ies", ies), ("nfcm", nfcm)):
            df.to_csv(out / f"{name}_clean.csv", index=False)
    return ghs, ies, nfcm


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["raw", "synthetic"], default=None)
    args = parser.parse_args()
    tables = build(args.mode)
    print({name: len(t) for name, t in zip(("ghs", "ies", "nfcm"), tables)})
