import pandas as pd
import pytest

from src.a_who_pays import affordability, revenue
from src.common.config import load_config
from src.common.pipeline import build


def _pool():
    ies = pd.DataFrame({
        "province": ["Gauteng"] * 4,
        "weight": [100.0, 100.0, 100.0, 100.0],
        "income": [1000.0, 2000.0, 4000.0, 8000.0],              # monthly rand
        "electricity_spend": [150.0, 100.0, 120.0, 160.0],       # monthly rand
    })
    return affordability.paying_households(ies)


def test_baby_steps_revenue():
    # shares of income: 15%, 5%, 3%, 2%. At a 10% line only the poorest cannot afford a bill.
    pool = _pool()
    nonpayers = {"Gauteng": 200.0}
    able, rev = revenue.revenue_for_pool(pool, nonpayers, 0.10, 1.0)
    # 3 of 4 households can afford, so 150 of the 200 non-payers; mean bill (100+120+160)/3 x 12
    assert able == pytest.approx(150.0)
    assert rev == pytest.approx(150.0 * (100 + 120 + 160) / 3 * 12)


def test_poorer_pool_gives_less_revenue():
    pool = _pool()
    nonpayers = {"Gauteng": 200.0}
    _, poor = revenue.revenue_for_pool(pool, nonpayers, 0.10, 0.5)
    _, all_ = revenue.revenue_for_pool(pool, nonpayers, 0.10, 1.0)
    assert poor < all_


def test_bounds_order():
    pool = _pool()
    b = revenue.revenue_bounds(pool, {"Gauteng": 200.0}, 0.10)
    assert b["poorest_first"][1] <= b["richest_first"][1]


def test_synthetic_table_and_collection_scaling():
    cfg = load_config()
    ghs, ies, _ = build("synthetic", save=False)
    table = revenue.revenue_table(ies, ghs, cfg)
    assert (table["revenue_rbn_low"] <= table["revenue_rbn_central"]).all()
    assert (table["revenue_rbn_central"] <= table["revenue_rbn_high"]).all()
    one = table[(table.threshold == 0.10) & (table.pool_share == 0.5)]
    full = one[one.collection_rate == 1.0]["revenue_rbn_central"].iloc[0]
    half = one[one.collection_rate == 0.5]["revenue_rbn_central"].iloc[0]
    assert half == pytest.approx(full * 0.5)


def test_supplier_shares_sum_to_one():
    ghs, _, _ = build("synthetic", save=False)
    assert sum(revenue.supplier_shares(ghs).values()) == pytest.approx(1.0)
