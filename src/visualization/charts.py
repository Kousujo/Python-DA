"""Biểu đồ Matplotlib cho báo cáo (CLO3, ≥3 biểu đồ có title/label/legend)."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from src.models.club import Club


def plot_participation_by_event(
    club: Club, save_path: str | None = None
) -> plt.Figure:
    """Biểu đồ cột: tỉ lệ tham gia theo sự kiện."""
    df = club.participation_rate_by_event().sort_values(
        "participation_rate", ascending=False
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(df["event_name"], df["participation_rate"] * 100, color="#4C72B0")
    ax.set_title("Tỉ lệ tham gia theo sự kiện")
    ax.set_xlabel("Sự kiện")
    ax.set_ylabel("Tỉ lệ tham gia (%)")
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df["event_name"], rotation=30, ha="right")
    for i, v in enumerate(df["participation_rate"] * 100):
        ax.text(i, v + 1, f"{v:.0f}%", ha="center", fontsize=8)
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
    return fig


def plot_member_growth(
    trend_df: pd.DataFrame, trend_stats: dict, save_path: str | None = None
) -> plt.Figure:
    """Biểu đồ đường: số thành viên tích lũy theo thời gian + đường xu hướng."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(
        trend_df["join_date"],
        trend_df["cumulative_members"],
        marker="o",
        label="Thực tế",
        color="#55A868",
    )
    ax.plot(
        trend_df["join_date"],
        trend_df["trend"],
        linestyle="--",
        label=f"Xu hướng ({trend_stats['slope']:.2f} thành viên/ngày)",
        color="#C44E52",
    )
    ax.set_title("Tăng trưởng thành viên theo thời gian")
    ax.set_xlabel("Ngày gia nhập")
    ax.set_ylabel("Số thành viên tích lũy")
    ax.legend()
    fig.autofmt_xdate(rotation=30)
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
    return fig


def plot_top_engaged_members(
    club: Club, top_n: int = 10, save_path: str | None = None
) -> plt.Figure:
    """Biểu đồ cột ngang: top thành viên tích cực nhất (điểm có trọng số đa hình)."""
    df = club.engagement_ranking(top_n=top_n).sort_values("engagement_score")
    colors = [
        "#DD8452" if "Ban chủ nhiệm" in role else "#4C72B0" for role in df["role"]
    ]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(df["member_name"], df["engagement_score"], color=colors)
    ax.set_title(f"Top {top_n} thành viên tích cực nhất")
    ax.set_xlabel("Điểm tích cực (có trọng số)")
    ax.set_ylabel("Thành viên")
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
    return fig


def plot_churn_risk(df: pd.DataFrame, save_path: str | None = None) -> plt.Figure:
    """Biểu đồ scatter: recency vs trend_drop, màu theo risk_level."""
    color_map = {"Nguy cơ cao": "#C44E52", "Ổn định": "#55A868", "Bình thường": "#4C72B0"}
    fig, ax = plt.subplots(figsize=(8, 6))
    for level, group in df.groupby("risk_level"):
        ax.scatter(
            group["recency_days"], group["trend_drop"],
            label=level, color=color_map.get(level, "#999999"), s=60,
        )
    high_risk = df[df["risk_level"] == "Nguy cơ cao"]
    for _, r in high_risk.iterrows():
        ax.annotate(r["member_name"], (r["recency_days"], r["trend_drop"]), fontsize=8)

    ax.set_title("Nguy cơ ngừng tham gia CLB")
    ax.set_xlabel("Số ngày chưa tham gia gần nhất")
    ax.set_ylabel("Mức giảm tỉ lệ tham gia (nửa đầu − nửa cuối)")
    ax.legend()
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
    return fig
