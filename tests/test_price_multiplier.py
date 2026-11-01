import numpy as np
import pandas as pd
import pytest

from src.a_who_pays import affordability, price_multiplier as pm
from src.common.pipeline import build


def _pool():
    ies = pd.DataFrame({
        "province": ["Gauteng"] * 2,
        "weight": [100.0, 100.0],
        "income": [1000.0, 2000.0],
        "electricity_spend": [50.0, 60.0],       # shares 5% and 3%
    })
    return affordability.paying_households(ies)


def test_baby_steps_price_doubles():
    # price doubles: shares become 10% and 6%. With a 10% line only the first is above it.
    assert pm.share_above(_pool(), 2.0, 0.10) == pytest.approx(0.5)


def test_demand_response_softens_the_burden():
    # elasticity -0.5: a doubling of price raises the bill by 2 ** 0.5, about 1.41
    assert pm.share_above(_pool(), 2.0, 0.10, elasticity=-0.5) == pytest.approx(0.0)


def test_share_rises_with_price():
    pool = affordability.paying_households(build("synthetic", save=False)[1])
    shares = [pm.share_above(pool, m, 0.10) for m in (1.0, 1.5, 2.0, 3.0)]
    assert shares == sorted(shares)


def test_crossing_multiplier_hits_target():
    pool = affordability.paying_households(build("synthetic", save=False)[1])
    m = pm.crossing_multiplier(pool, 0.10)
    assert pm.share_above(pool, m, 0.10) >= 0.5 - 1e-6
    assert pm.share_above(pool, m * 0.99, 0.10) < 0.5


def test_years_formula():
    # doubling at 7% a year takes about 10.2 years
    assert pm.years_to_reach(2.0, 1.0, 0.07) == pytest.approx(np.log(2) / np.log(1.07))
    assert pm.years_to_reach(2.0, 1.0, 0.07) == pytest.approx(10.24, abs=0.01)
