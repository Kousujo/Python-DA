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