"""Notebook 03: registered indigent households versus households that qualify on income."""
import numpy as np
import pandas as pd


def qualifying_by_province(ies, cutoff):
    """Weighted count of households with monthly income at or below the cut-off."""
    below = ies[ies["income"] <= cutoff]
    return below.groupby("province")["weight"].sum().rename("qualifying_households")


def coverage_table(ies, nfcm, cutoffs):
    """Coverage = registered / qualifying, for each income cut-off tested."""
    registered = nfcm.set_index("province")[["indigent_registered"]]
    frames = []
    for cutoff in cutoffs:
        table = registered.join(qualifying_by_province(ies, cutoff), how="outer").fillna(0)
        table["cutoff_rand"] = cutoff
        qualifying = table["qualifying_households"]
        table["coverage"] = table["indigent_registered"] / qualifying.replace(0, np.nan)
        table["gap_households"] = (qualifying - table["indigent_registered"]).clip(lower=0)
        frames.append(table.reset_index())
    return pd.concat(frames, ignore_index=True)
