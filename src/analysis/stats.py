"""Phân tích thống kê nâng cao (SciPy) trên dữ liệu từ Club.

Tầng này KHÔNG chứa logic OOP, chỉ nhận Club đã build sẵn (từ
models/club.py, sau khi loader.py nạp dữ liệu) và làm phân tích bổ
sung: xu hướng tăng trưởng, phân loại thành viên bằng thống kê.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from src.models.club import Club


def growth_trend(club: Club) -> tuple[pd.DataFrame, dict[str, float]]:
    """Xu hướng tăng trưởng thành viên theo thời gian bằng hồi quy tuyến tính.

    Trả về:
        - DataFrame (join_date, cumulative_members) kèm cột 'trend' —
          giá trị dự đoán theo đường hồi quy, dùng để vẽ overlay trên
          biểu đồ đường.
        - dict thống kê: slope (thành viên/ngày), intercept, r_value,
          p_value, std_err — dùng để giải thích xu hướng trong báo cáo.
    """
    df = club.member_growth_over_time()
    if df.empty or len(df) < 2:
        return df.assign(trend=np.nan), {
            "slope": 0.0,
            "intercept": 0.0,
            "r_value": 0.0,
            "p_value": 1.0,
            "std_err": 0.0,
        }

    join_dates = pd.to_datetime(df["join_date"])
    x = (join_dates - join_dates.min()).dt.days
    y = df["cumulative_members"]

    result = stats.linregress(x, y)
    df = df.copy()
    df["trend"] = result.intercept + result.slope * x

    return df, {
        "slope": result.slope,
        "intercept": result.intercept,
        "r_value": result.rvalue,
        "p_value": result.pvalue,
        "std_err": result.stderr,
    }


def engagement_with_stats(
    club: Club, z_threshold: float = 1.0
) -> pd.DataFrame:
    """engagement_ranking() bổ sung z-score, percentile và phân loại thống kê.

    Phân loại:
        - 'Nổi bật'       nếu z-score >= z_threshold
        - 'Cần khích lệ'  nếu z-score <= -z_threshold
        - 'Bình thường'   còn lại
    """
    df = club.engagement_ranking().reset_index(drop=True)
    if df.empty or df["engagement_score"].std(ddof=0) == 0:
        df = df.copy()
        df["z_score"] = 0.0
        df["percentile"] = 100.0
        df["classification"] = "Bình thường"
        return df

    df = df.copy()
    df["z_score"] = stats.zscore(df["engagement_score"])
    df["percentile"] = df["engagement_score"].rank(pct=True) * 100

    def classify(z: float) -> str:
        if z >= z_threshold:
            return "Nổi bật"
        if z <= -z_threshold:
            return "Cần khích lệ"
        return "Bình thường"

    df["classification"] = df["z_score"].apply(classify)
    return df


def churn_risk(club: Club, z_threshold: float = 1.0) -> pd.DataFrame:
    """Ước lượng nguy cơ ngừng tham gia CLB.

    2 yếu tố, chuẩn hoá z-score:
      - recency_days: số ngày kể từ lần tham gia gần nhất đến sự kiện
        cuối cùng trong dữ liệu (chưa từng tham gia = stale tối đa).
      - trend_drop: tỉ lệ tham gia nửa đầu khoảng thời gian - nửa cuối
        (dương = đang giảm dần).
    churn_score = trung bình 2 z-score, phân loại theo z_threshold,
    đồng bộ phong cách với engagement_with_stats().
    """
    if not club._events:
        return pd.DataFrame()

    event_dates = sorted(e.date for e in club._events.values())
    last_date = event_dates[-1]
    first_date = event_dates[0]
    mid_date = event_dates[len(event_dates) // 2]

    first_half_ids = {eid for eid, e in club._events.items() if e.date <= mid_date}
    second_half_ids = {eid for eid, e in club._events.items() if e.date > mid_date}

    df = club.to_dataframe()

    rows = []
    for member_id, member in club._members.items():
        attended = df[df["member_id"] == member_id]
        if attended.empty:
            recency_days = (last_date - first_date).days
            rate_first = rate_second = 0.0
        else:
            last_attend_date = pd.to_datetime(attended["checkin_time"]).max().date()
            recency_days = (last_date - last_attend_date).days
            attended_ids = set(attended["event_id"])
            rate_first = (
                len(attended_ids & first_half_ids) / len(first_half_ids)
                if first_half_ids else 0.0
            )
            rate_second = (
                len(attended_ids & second_half_ids) / len(second_half_ids)
                if second_half_ids else 0.0
            )
        rows.append(
            {
                "member_id": member_id,
                "member_name": member.full_name,
                "recency_days": recency_days,
                "trend_drop": rate_first - rate_second,
            }
        )

    result = pd.DataFrame(rows)
    if len(result) < 2 or result["recency_days"].std(ddof=0) == 0:
        result["churn_score"] = 0.0
    else:
        z_recency = stats.zscore(result["recency_days"])
        z_trend = stats.zscore(result["trend_drop"])
        result["churn_score"] = (z_recency + z_trend) / 2

    result["risk_level"] = result["churn_score"].apply(
        lambda z: (
            "Nguy cơ cao" if z >= z_threshold
            else "Ổn định" if z <= -z_threshold
            else "Bình thường"
        )
    )
    return result.sort_values("churn_score", ascending=False)
