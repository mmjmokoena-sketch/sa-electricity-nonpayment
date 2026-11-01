"""Simple, consistent charts saved as PNG files."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def _finish(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def threshold_curve(grid, headline, path):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(grid["threshold"] * 100, grid["share_above"] * 100, marker="o")
    ax.axvline(headline * 100, linestyle="--", color="grey")
    ax.set_xlabel("Affordability threshold (electricity bill as % of income)")
    ax.set_ylabel("Households above threshold (%)")
    ax.set_title("Share of households with an unaffordable bill")
    _finish(fig, path)


def coverage_bars(cov, cutoff, path):
    data = cov[cov["cutoff_rand"] == cutoff].sort_values("coverage")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(data["province"], data["coverage"] * 100)
    ax.set_xlabel(f"Registered indigent as % of households earning <= R{cutoff:,}/month")
    ax.set_title("Indigent registration coverage by province")
    _finish(fig, path)


def split_ranges(summary, path):
    fig, ax = plt.subplots(figsize=(7, 4))
    labels = [f"{t * 100:.0f}% threshold" for t in summary["threshold"]]
    mid = summary["able_share_mid"] * 100
    low = mid - summary["able_share_low"] * 100
    high = summary["able_share_high"] * 100 - mid
    ax.errorbar(mid, labels, xerr=[low, high], fmt="o", capsize=5)
    ax.set_xlabel("Non-paying households able to pay (%): low / mid / high bound")
    ax.set_title("Can't pay versus won't pay")
    _finish(fig, path)


def counterfactual_bars(cf, path):
    fig, ax = plt.subplots(figsize=(7, 4))
    for u, g in cf.groupby("unpaid_share"):
        ax.plot(g["able_share"] * 100, g["change_vs_payers_only_pct"], marker="o",
                label=f"unpaid volume {u * 100:.1f}%")
    ax.set_xlabel("Share of non-payers able to pay and now paying (%)")
    ax.set_ylabel("Change in price paid by payers (%)")
    ax.set_title("Counterfactual tariff")
    ax.legend()
    _finish(fig, path)


def multiplier_curve(table, headline_pct, path):
    fig, ax = plt.subplots(figsize=(7, 4))
    for col in [c for c in table.columns if c.startswith("share_above_")]:
        label = col.replace("share_above_", "").replace("pct", "% of income")
        ax.plot(table["multiplier"], table[col] * 100, marker="o", label=label,
                linewidth=2.5 if col == f"share_above_{headline_pct}pct" else 1.2)
    ax.axhline(50, linestyle="--", color="grey")
    ax.set_xlabel("Real price relative to income (1.0 = survey year)")
    ax.set_ylabel("Households with a bill above the line (%)")
    ax.set_title("When do most households face an unaffordable bill?")
    ax.legend(title="Bill at least")
    _finish(fig, path)


def revenue_range(rev, threshold, path):
    data = rev[(rev["threshold"] == threshold) & (rev["collection_rate"] == 1.0)]
    data = data.sort_values("pool_share")
    labels = [f"poorest {int(p * 100)}%" if p < 1 else "typical payer" for p in data["pool_share"]]
    fig, ax = plt.subplots(figsize=(7, 4))
    central = data["revenue_rbn_central"].values
    err = [central - data["revenue_rbn_low"].values, data["revenue_rbn_high"].values - central]
    ax.bar(labels, central, yerr=err, capsize=5)
    ax.set_ylabel("Revenue if all able-to-pay non-payers paid (R bn a year)")
    ax.set_xlabel("Non-payers assumed to be drawn from...")
    ax.set_title(f"Revenue scenarios, 2025/26 prices (threshold {int(threshold * 100)}%)")
    _finish(fig, path)
