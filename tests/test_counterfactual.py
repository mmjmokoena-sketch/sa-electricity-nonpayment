from src.a_who_pays.counterfactual import (
    counterfactual_tariff, payers_only_tariff, pct_change)


def test_baby_steps_example():
    # costs R100, 90 units paid, 10 unpaid, half of the unpaid can afford to pay
    t = payers_only_tariff(100, 90)
    t_new = counterfactual_tariff(100, 90, 10, 0.5)
    assert abs(t - 1.1111) < 1e-3
    assert abs(t_new - 1.0526) < 1e-3
    assert abs(pct_change(t, t_new) + 5.26) < 0.05


def test_practice_question():
    t = payers_only_tariff(200, 160)
    t_new = counterfactual_tariff(200, 160, 40, 0.25)
    assert abs(t - 1.25) < 1e-9
    assert abs(t_new - 1.1765) < 1e-3
    assert abs(pct_change(t, t_new) + 5.88) < 0.05


def test_no_able_payers_means_no_change():
    assert counterfactual_tariff(100, 90, 10, 0.0) == payers_only_tariff(100, 90)
