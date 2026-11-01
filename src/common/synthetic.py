"""FAKE data for testing the pipeline before the real files are downloaded.

Nothing built from this module is real. Never publish results made from it.
"""
import numpy as np
import pandas as pd

PROVINCES = ["Western Cape", "Eastern Cape", "Northern Cape", "Free State", "KwaZulu-Natal",
             "North West", "Gauteng", "Mpumalanga", "Limpopo"]
SHARES = [0.11, 0.11, 0.02, 0.05, 0.17, 0.07, 0.26, 0.08, 0.13]


def make_synthetic(cfg, seed=42, n=6000):
    rng = np.random.default_rng(seed)
    cm = cfg["column_map"]
    div = cfg["units"]["ies_income_divisor"]

    # Income survey: bill share falls as income rises (the usual pattern)
    income = rng.lognormal(mean=9.2, sigma=1.1, size=n)
    noise = rng.lognormal(mean=0.0, sigma=0.15, size=n)
    spend = 0.06 * (income / 10000) ** -0.5 * income * noise
    spend = np.clip(spend, 0, income * 0.5)
    spend[rng.random(n) < 0.05] = 0.0
    ies = pd.DataFrame({
        cm["ies"]["province"]: rng.choice(PROVINCES, size=n, p=SHARES),
        cm["ies"]["weight"]: rng.uniform(1500, 3500, n),
        cm["ies"]["income"]: income * div,
        cm["ies"]["electricity_spend"]: spend * div,
    })

    # Household survey: province codes 1-9, payment codes 1 yes / 2 no / 8 not applicable
    codes = rng.choice(np.arange(1, 10), size=n, p=SHARES)
    draw = rng.random(n)
    pays = np.where(draw < 0.78, 1, np.where(draw < 0.91, 2, 8))
    ghs_cols = {
        cm["ghs"]["province"]: codes,
        cm["ghs"]["weight"]: rng.uniform(1500, 3500, n),
        cm["ghs"]["pays_electricity"]: pays,
    }
    if "supplier" in cm["ghs"]:
        ghs_cols[cm["ghs"]["supplier"]] = rng.choice([1, 2, 3, 4], size=n, p=[0.45, 0.5, 0.03, 0.02])
    ghs = pd.DataFrame(ghs_cols)

    # Municipal census: indigent registrations by province
    registered = rng.integers(80_000, 500_000, size=9)
    nfcm = pd.DataFrame({
        cm["nfcm"]["province"]: PROVINCES,
        cm["nfcm"]["indigent_registered"]: registered,
        cm["nfcm"]["fbe_households"]: (registered * 0.8).astype(int),
    })
    return {"ghs": ghs, "ies": ies, "nfcm": nfcm}
