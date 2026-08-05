"""Pipeline chính: load dữ liệu → phân tích → xuất biểu đồ."""

from __future__ import annotations

import sys
from pathlib import Path

from src.analysis.stats import engagement_with_stats, growth_trend
from src.processing.loader import load_club_from_csv
from src.visualization.charts import (
    plot_member_growth,
    plot_participation_by_event,
    plot_top_engaged_members,
)

FIGURES_DIR = Path("report/figures")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    club = load_club_from_csv("data/raw")

    print("=== Tỉ lệ tham gia theo sự kiện ===")
    print(club.participation_rate_by_event().to_string(index=False))

    print("\n=== Tỉ lệ tham gia theo thành viên ===")
    print(club.participation_rate_by_member().to_string(index=False))

    trend_df, trend_stats = growth_trend(club)
    print("\n=== Xu hướng tăng trưởng thành viên ===")
    print(
        f"slope={trend_stats['slope']:.3f} thành viên/ngày, "
        f"r={trend_stats['r_value']:.3f}, p={trend_stats['p_value']:.4f}"
    )

    print("\n=== Xếp hạng thành viên tích cực (kèm thống kê) ===")
    print(engagement_with_stats(club).to_string(index=False))

    plot_participation_by_event(club, str(FIGURES_DIR / "participation_by_event.png"))
    plot_member_growth(trend_df, trend_stats, str(FIGURES_DIR / "member_growth.png"))
    plot_top_engaged_members(club, save_path=str(FIGURES_DIR / "top_members.png"))
    print(f"\nĐã lưu 3 biểu đồ vào {FIGURES_DIR}/")


if __name__ == "__main__":
    main()