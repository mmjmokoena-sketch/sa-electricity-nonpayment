from src.a_who_pays import affordability, split
from src.common.pipeline import build
from src.common.synthetic import PROVINCES


def test_synthetic_pipeline_builds_clean_tables():
    ghs, ies, nfcm = build("synthetic", save=False)
    assert set(ghs["province"]) == set(PROVINCES)
    assert (ies["weight"] > 0).all() and (ies["income"] > 0).all()
    assert set(ghs["pays_electricity"]) <= {"yes", "no"}
    assert len(nfcm) == 9


def test_threshold_share_falls_as_threshold_rises():
    _, ies, _ = build("synthetic", save=False)
    table = affordability.threshold_table(ies, [0.05, 0.10, 0.20])
    shares = list(table["share_above"])
    assert shares == sorted(shares, reverse=True)


def test_split_bounds_stay_within_nonpayers():
    ghs, ies, _ = build("synthetic", save=False)
    bounds = split.unable_bounds(ies, split.nonpayers_by_province(ghs), 0.10)
    for col in ("unable_poorest_first", "unable_random", "unable_richest_first"):
        assert (bounds[col] >= 0).all()
        assert (bounds[col] <= bounds["nonpayers"] + 1e-6).all()
    summary = split.split_summary(bounds, 0.10)
    assert summary["able_to_pay_low"] <= summary["able_to_pay_high"] + 1e-6
