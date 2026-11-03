from src.a_who_pays import affordability, robustness
from src.common.config import load_config
from src.common.pipeline import build


def test_checks_run_on_synthetic_data():
    cfg = load_config()
    ghs, ies, _ = build("synthetic", save=False)
    table = robustness.run_checks(ies, ghs, cfg)
    assert len(table) >= 5
    assert table["baseline"].notna().all() and table["alternative"].notna().all()
    shares = table[table["unit"] == "share"]
    assert shares["baseline"].between(0, 1).all() and shares["alternative"].between(0, 1).all()


def test_two_smallest_provinces_are_returned():
    _, ies, _ = build("synthetic", save=False)
    assert len(robustness.smallest_provinces(ies, 2)) == 2


def test_unweighted_and_weighted_agree_when_weights_equal():
    _, ies, _ = build("synthetic", save=False)
    pool = affordability.paying_households(ies.assign(weight=1.0))
    assert abs(robustness.share_above(pool, 0.10) - robustness.share_above(pool, 0.10, weighted=False)) < 1e-12
