"""Interactive scenario explorer for Project A (run with: streamlit run dashboards/app.py).

Reads only aggregated tables from projects/a_who_pays/outputs/tables, never raw microdata.
"""
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.a_who_pays.counterfactual import (  # noqa: E402
    counterfactual_tariff, payers_only_tariff, pct_change)
from src.common.config import load_config  # noqa: E402

TABLES = ROOT / "projects" / "a_who_pays" / "outputs" / "tables"
cfg = load_config()
tariff = cfg["tariff"]

st.set_page_config(page_title="SA electricity non-payment: Project A", layout="wide")
st.title("Who pays for electricity non-payment in South Africa?")
st.caption("Scenario estimates, not forecasts. Every assumption is adjustable on the left. "
           "Sources and method: see the project repository.")


@st.cache_data
def read_table(name):
    path = TABLES / name
    return pd.read_csv(path) if path.exists() else None


with st.sidebar:
    st.header("Assumptions")
    unpaid = st.slider("Share of billed volume that is not paid for", 0.01, 0.20,
                       float(tariff["headline_unpaid_share"]), 0.001, format="%.3f")
    able = st.slider("Share of non-payers able to pay", 0.0, 1.0,
                     float(cfg["scenarios"]["headline_share"]), 0.05)
    threshold = st.select_slider("Affordability threshold (bill as % of income)",
                                 options=[round(x / 100, 2) for x in range(5, 21)],
                                 value=cfg["thresholds"]["headline"])

cost = tariff["allowable_revenue_rand_bn"] * 1e9
q_total = tariff["sales_volume_gwh"] * 1e6
q_unpaid = unpaid * q_total
q_paid = q_total - q_unpaid
t_payers = payers_only_tariff(cost, q_paid)
t_cf = counterfactual_tariff(cost, q_paid, q_unpaid, able)

c1, c2, c3 = st.columns(3)
c1.metric("Price if payers cover all costs", f"{t_payers * 100:.1f} c/kWh")
c2.metric("Price if able-to-pay non-payers paid", f"{t_cf * 100:.1f} c/kWh",
          f"{pct_change(t_payers, t_cf):.1f}%")
recoverable = able * unpaid * tariff["allowable_revenue_rand_bn"]
c3.metric("Revenue recoverable per year", f"R{recoverable:.1f}bn")

left, right = st.columns(2)
grid = read_table("threshold_grid.csv")
if grid is not None:
    fig = px.line(grid, x=grid["threshold"] * 100, y=grid["share_above"] * 100,
                  labels={"x": "Threshold (% of income)", "y": "Households above (%)"},
                  title="Households with an unaffordable electricity bill")
    fig.add_vline(x=threshold * 100, line_dash="dash")
    left.plotly_chart(fig, width="stretch")
else:
    left.info("Run the analysis first to create threshold_grid.csv")

coverage = read_table("indigent_coverage.csv")
if coverage is not None:
    cutoff = cfg["indigent"]["headline_cutoff_rand"]
    data = coverage[coverage["cutoff_rand"] == cutoff].sort_values("coverage")
    fig = px.bar(data, x=data["coverage"] * 100, y="province", orientation="h",
                 labels={"x": "Registered as % of qualifying households"},
                 title=f"Indigent registration coverage (income up to R{cutoff:,}/month)")
    right.plotly_chart(fig, width="stretch")

split = read_table("split_summary.csv")
if split is not None:
    st.subheader("Can't pay versus won't pay (non-paying households able to pay)")
    st.dataframe(split.round(3), width="stretch")
