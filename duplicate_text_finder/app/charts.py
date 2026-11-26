"""Matplotlib chart generation for analytics and trend visualization."""

from __future__ import annotations

import io
import os
import tempfile
from pathlib import Path
from typing import Literal

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "dtf_mplconfig"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from app.models import SummaryMetrics

ChartKind = Literal["distribution", "categories", "trends"]

PALETTE = {
    "bg": "#ffffff",
    "text": "#1e293b",
    "muted": "#64748b",
    "grid": "#e2e8f0",
    "unique": "#0f766e",
    "duplicate": "#dc2626",
    "accent": "#2563eb",
}


def _empty_chart_bytes(title: str, message: str = "No stored records available yet.") -> bytes:
    """Render a clean informative figure when no data is present."""
    fig, ax = plt.subplots(figsize=(6.8, 4.0), dpi=130)
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["bg"])
    ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", color=PALETTE["text"], pad=12)
    ax.text(
        0.5,
        0.5,
        message,
        ha="center",
        va="center",
        fontsize=11,
        color=PALETTE["muted"],
        transform=ax.transAxes,
    )
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def render_chart_png(metrics: SummaryMetrics, kind: ChartKind) -> bytes:
    """Generate a PNG chart image from live SummaryMetrics using Matplotlib."""
    if metrics.total_records == 0:
        titles = {
            "distribution": "Unique vs. Duplicate Entries",
            "categories": "Records & Duplicates by Category",
            "trends": "Daily Record & Duplication Trend",
        }
        return _empty_chart_bytes(titles.get(kind, "Analytics Chart"))

    if kind == "distribution":
        return _render_distribution_chart(metrics)
    if kind == "categories":
        return _render_category_chart(metrics)
    if kind == "trends":
        return _render_trend_chart(metrics)
    raise ValueError(f"Unsupported chart kind: {kind}")


def _render_distribution_chart(metrics: SummaryMetrics) -> bytes:
    fig, ax = plt.subplots(figsize=(6.8, 4.2), dpi=130)
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["bg"])

    labels = ["Unique Entries", "Duplicate Entries"]
    values = [metrics.unique_entries, metrics.duplicate_entries]
    colors = [PALETTE["unique"], PALETTE["duplicate"]]

    # Handle case where one slice is 0 so pie chart stays crisp
    non_zero = [(lbl, val, col) for lbl, val, col in zip(labels, values, colors) if val > 0]
    plot_labels = [item[0] for item in non_zero]
    plot_values = [item[1] for item in non_zero]
    plot_colors = [item[2] for item in non_zero]

    wedges, texts, autotexts = ax.pie(
        plot_values,
        labels=plot_labels,
        colors=plot_colors,
        autopct=lambda pct: f"{pct:.1f}%",
        startangle=140,
        pctdistance=0.75,
        wedgeprops={"width": 0.42, "edgecolor": "white", "linewidth": 2},
        textprops={"color": PALETTE["text"], "fontsize": 10},
    )
    for auto in autotexts:
        auto.set_color("white")
        auto.set_fontweight("bold")
        auto.set_fontsize(9.5)

    ax.text(
        0,
        0,
        f"{metrics.total_records}\nTotal",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        color=PALETTE["text"],
    )
    ax.set_title(
        f"Unique ({metrics.unique_entries}) vs. Exact Duplicates ({metrics.duplicate_entries})",
        fontsize=12,
        fontweight="bold",
        color=PALETTE["text"],
        pad=12,
    )

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def _render_category_chart(metrics: SummaryMetrics) -> bytes:
    categories = [row["category"] for row in metrics.category_breakdown]
    unique_counts = [row["unique"] for row in metrics.category_breakdown]
    dup_counts = [row["duplicates"] for row in metrics.category_breakdown]

    fig, ax = plt.subplots(figsize=(7.2, max(4.0, len(categories) * 0.48 + 1.4)), dpi=130)
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["bg"])

    y_pos = list(range(len(categories)))
    ax.barh(y_pos, unique_counts, color=PALETTE["unique"], label="Unique", height=0.6)
    ax.barh(
        y_pos,
        dup_counts,
        left=unique_counts,
        color=PALETTE["duplicate"],
        label="Exact Duplicates",
        height=0.6,
    )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories, fontsize=9.5, color=PALETTE["text"])
    ax.invert_yaxis()
    ax.set_xlabel("Record Count", fontsize=10, color=PALETTE["muted"])
    ax.set_title("Records & Exact Duplicates by Category", fontsize=12, fontweight="bold", color=PALETTE["text"], pad=12)
    ax.grid(axis="x", linestyle="--", alpha=0.6, color=PALETTE["grid"])
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, loc="lower right", fontsize=9)

    for idx, (u_val, d_val) in enumerate(zip(unique_counts, dup_counts)):
        total = u_val + d_val
        ax.text(total + 0.15, idx, str(total), va="center", fontsize=8.5, color=PALETTE["text"])

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def _render_trend_chart(metrics: SummaryMetrics) -> bytes:
    trends = metrics.daily_trends
    dates = [row["date"] for row in trends]
    totals = [row["total"] for row in trends]
    dups = [row["duplicates"] for row in trends]

    fig, ax = plt.subplots(figsize=(7.4, 4.2), dpi=130)
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["bg"])

    x = list(range(len(dates)))
    ax.plot(x, totals, marker="o", linewidth=2.2, color=PALETTE["accent"], label="Total Records")
    ax.plot(x, dups, marker="s", linewidth=2.0, color=PALETTE["duplicate"], label="Duplicate Records")
    ax.fill_between(x, dups, color=PALETTE["duplicate"], alpha=0.12)

    ax.set_xticks(x)
    ax.set_xticklabels(dates, rotation=28, ha="right", fontsize=8.5, color=PALETTE["text"])
    ax.set_ylabel("Number of Records", fontsize=10, color=PALETTE["muted"])
    ax.set_title("Daily Submission & Duplication Trend", fontsize=12, fontweight="bold", color=PALETTE["text"], pad=12)
    ax.grid(axis="y", linestyle="--", alpha=0.6, color=PALETTE["grid"])
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, loc="upper left", fontsize=9)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()
