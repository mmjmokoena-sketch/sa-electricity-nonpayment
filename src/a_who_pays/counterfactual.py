"""Notebook 05: what would payers be charged if able-to-pay non-payers paid?

Stylised full-recovery counterfactual (an economic burden measure, not the legal tariff):
  t  = C / Q_p                 costs recovered only from paying volume
  t' = C / (Q_p + s * Q_n)     a share s of unpaid volume now pays
"""
import pandas as pd


def payers_only_tariff(cost, q_paid):
    return cost / q_paid


def counterfactual_tariff(cost, q_paid, q_unpaid, able_share):
    return cost / (q_paid + able_share * q_unpaid)


def pct_change(old, new):
    return (new - old) / old * 100


def scenario_grid(cfg):
    """Run every combination of unpaid share (u) and able-to-pay share (s)."""
    tariff = cfg["tariff"]
    cost = tariff["allowable_revenue_rand_bn"] * 1e9      # rand
    q_total = tariff["sales_volume_gwh"] * 1e6             # kWh
    official = cost / q_total                              # rand per kWh
    rows = []
    for u in tariff["unpaid_share_of_volume"]:
        q_unpaid = u * q_total
        q_paid = q_total - q_unpaid
        t_payers = payers_only_tariff(cost, q_paid)
        for s in cfg["scenarios"]["able_to_pay_share"]:
            t_cf = counterfactual_tariff(cost, q_paid, q_unpaid, s)
            rows.append({
                "unpaid_share": u, "able_share": s,
                "tariff_official_c_per_kwh": official * 100,
                "tariff_payers_only_c_per_kwh": t_payers * 100,
                "tariff_counterfactual_c_per_kwh": t_cf * 100,
                "change_vs_payers_only_pct": pct_change(t_payers, t_cf),
                "recoverable_rand_bn": s * u * tariff["allowable_revenue_rand_bn"],
            })
    return pd.DataFrame(rows)
