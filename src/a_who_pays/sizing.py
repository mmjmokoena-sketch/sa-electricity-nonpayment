"""Notebook 01: put the different non-payment measures side by side."""
import pandas as pd

REQUIRED = ["measure", "date", "value", "unit", "source", "verified"]


def load_measures(path):
    df = pd.read_csv(path)
    missing = [col for col in REQUIRED if col not in df.columns]
    if missing:
        raise KeyError(f"Missing columns in {path}: {missing}")
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values(["measure", "date"]).reset_index(drop=True)


def latest_by_measure(df):
    return df.sort_values("date").groupby("measure").tail(1).reset_index(drop=True)


def annual_growth(df, measure):
    """Compound annual growth rate between the first and last observation of a measure."""
    rows = df[df["measure"] == measure].sort_values("date")
    if len(rows) < 2:
        return float("nan")
    years = (rows["date"].iloc[-1] - rows["date"].iloc[0]).days / 365.25
    ratio = rows["value"].iloc[-1] / rows["value"].iloc[0]
    return float(ratio ** (1 / years) - 1)
