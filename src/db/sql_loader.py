"""Tạo schema SQL Server + nạp dữ liệu từ data/raw, cộng vài query demo
(JOIN/GROUP BY/window function) đối chiếu lại kết quả engagement_ranking
của Python.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import Engine, create_engine, text

from src.config import get_sql_connection_string

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_engine() -> Engine:
    return create_engine(get_sql_connection_string())


def create_schema(engine: Engine) -> None:
    """Chạy schema.sql — xoá và tạo lại 3 bảng."""
    sql_script = SCHEMA_PATH.read_text(encoding="utf-8")
    with engine.begin() as conn:
        for statement in sql_script.split(";"):
            if statement.strip():
                conn.execute(text(statement))


def load_csv_to_sql(engine: Engine, data_dir: str | Path = "data/raw") -> None:
    """Nạp 3 CSV vào 3 bảng đã tạo. Lọc bỏ attendance không khớp FK.
    Dùng INSERT thủ công từng dòng thay vì to_sql() để tránh một dòng
    vi phạm FK làm chết cả batch insert (to_sql() theo mặc định gộp
    nhiều dòng vào một lệnh, gặp lỗi là hỏng hết).
    """
    data_dir = Path(data_dir)

    members_df = pd.read_csv(data_dir / "members.csv", dtype=str, encoding="utf-8")
    events_df = pd.read_csv(data_dir / "events.csv", dtype=str, encoding="utf-8")
    attendance_df = pd.read_csv(data_dir / "attendance.csv", dtype=str, encoding="utf-8")

    with engine.begin() as conn:
        # Members
        for _, row in members_df.iterrows():
            conn.execute(
                text(
                    "INSERT INTO dbo.Members (member_id, full_name, class_name, join_date, role, position) "
                    "VALUES (:member_id, :full_name, :class_name, :join_date, :role, :position)"
                ),
                {
                    "member_id": row["member_id"],
                    "full_name": row["full_name"],
                    "class_name": row["class_name"] if pd.notna(row["class_name"]) else None,
                    "join_date": row["join_date"],
                    "role": row["role"],
                    "position": row["position"] if pd.notna(row["position"]) else None,
                },
            )

        # Events
        for _, row in events_df.iterrows():
            conn.execute(
                text(
                    "INSERT INTO dbo.Events (event_id, name, date, category, event_type) "
                    "VALUES (:event_id, :name, :date, :category, :event_type)"
                ),
                {
                    "event_id": row["event_id"],
                    "name": row["name"],
                    "date": row["date"],
                    "category": row["category"] if pd.notna(row["category"]) else None,
                    "event_type": row["event_type"],
                },
            )

        # Attendance - filter FK
        valid_member_ids = set(members_df["member_id"])
        valid_event_ids = set(events_df["event_id"])
        valid_attendance = attendance_df[
            attendance_df["member_id"].isin(valid_member_ids)
            & attendance_df["event_id"].isin(valid_event_ids)
        ]
        if len(valid_attendance) < len(attendance_df):
            print(
                f"Đã lọc bỏ {len(attendance_df) - len(valid_attendance)} "
                f"dòng attendance không khớp FK."
            )

        for _, row in valid_attendance.iterrows():
            conn.execute(
                text(
                    "INSERT INTO dbo.Attendance (member_id, event_id, checkin_time) "
                    "VALUES (:member_id, :event_id, :checkin_time)"
                ),
                {
                    "member_id": row["member_id"],
                    "event_id": row["event_id"],
                    "checkin_time": row["checkin_time"],
                },
            )


def query_participation_detail(engine: Engine) -> pd.DataFrame:
    """JOIN 3 bảng — chi tiết từng lượt điểm danh."""
    sql = """
        SELECT m.full_name, m.role, e.name AS event_name,
               e.event_type, a.checkin_time
        FROM dbo.Attendance a
        JOIN dbo.Members m ON m.member_id = a.member_id
        JOIN dbo.Events e ON e.event_id = a.event_id
        ORDER BY a.checkin_time
    """
    return pd.read_sql(sql, engine)


def query_attendance_count_by_event(engine: Engine) -> pd.DataFrame:
    """GROUP BY — số người điểm danh mỗi sự kiện."""
    sql = """
        SELECT e.event_id, e.name, COUNT(a.member_id) AS attendee_count
        FROM dbo.Events e
        LEFT JOIN dbo.Attendance a ON a.event_id = e.event_id
        GROUP BY e.event_id, e.name
        ORDER BY attendee_count DESC
    """
    return pd.read_sql(sql, engine)


def query_member_rank_window(engine: Engine) -> pd.DataFrame:
    """Window function RANK() — xếp hạng điểm tích cực, công thức khớp
    engagement_ranking() bên Python (trọng số 1.5/0.8, hệ số officer 1.2)
    để đối chiếu hai kết quả trong báo cáo.
    """
    sql = """
        WITH member_scores AS (
            SELECT
                m.member_id, m.full_name, m.role,
                SUM(CASE WHEN e.event_type = 'mandatory' THEN 1.5 ELSE 0.8 END)
                    * CASE WHEN m.role = 'officer' THEN 1.2 ELSE 1.0 END
                    AS engagement_score
            FROM dbo.Attendance a
            JOIN dbo.Members m ON m.member_id = a.member_id
            JOIN dbo.Events e ON e.event_id = a.event_id
            GROUP BY m.member_id, m.full_name, m.role
        )
        SELECT *, RANK() OVER (ORDER BY engagement_score DESC) AS rank_in_club
        FROM member_scores
        ORDER BY rank_in_club
    """
    return pd.read_sql(sql, engine)


if __name__ == "__main__":
    from src.config import setup_utf8_stdout

    setup_utf8_stdout()
    engine = get_engine()
    create_schema(engine)
    load_csv_to_sql(engine)
    print(query_attendance_count_by_event(engine).to_string(index=False))
    print(query_member_rank_window(engine).to_string(index=False))