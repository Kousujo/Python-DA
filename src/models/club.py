"""Club — lớp điều phối, tổng hợp (composition) Member và Event.

Club không kế thừa từ đâu; nó SỬ DỤNG đa hình của Member/Event (gọi
get_score_multiplier() / get_attendance_weight() qua interface chung)
mà không cần biết đối tượng cụ thể là lớp con nào.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from src.models.event import Event
from src.models.exceptions import (
    DuplicateAttendanceError,
    EventNotFoundError,
    MemberNotFoundError,
)
from src.models.member import Member


@dataclass
class AttendanceRecord:
    """Một lượt điểm danh: thành viên nào, sự kiện nào, lúc nào."""

    member_id: str
    event_id: str
    checkin_time: datetime


class Club:
    """Quản lý danh sách Member, Event và lịch sử điểm danh của câu lạc bộ."""

    def __init__(self) -> None:
        self._members: dict[str, Member] = {}
        self._events: dict[str, Event] = {}
        self._attendance: list[AttendanceRecord] = []

    # -- Đăng ký dữ liệu ------------------------------------------------
    def add_member(self, member: Member) -> None:
        self._members[member.member_id] = member

    def add_event(self, event: Event) -> None:
        self._events[event.event_id] = event

    # -- Điểm danh --------------------------------------------------------
    def check_in(self, member_id: str, event_id: str, checkin_time: datetime) -> None:
        """Ghi nhận điểm danh. Ném exception nếu dữ liệu không hợp lệ."""
        if member_id not in self._members:
            raise MemberNotFoundError(member_id)
        if event_id not in self._events:
            raise EventNotFoundError(event_id)
        if any(
            r.member_id == member_id and r.event_id == event_id
            for r in self._attendance
        ):
            raise DuplicateAttendanceError(member_id, event_id)
        self._attendance.append(AttendanceRecord(member_id, event_id, checkin_time))

    # -- Tổng hợp dữ liệu ---------------------------------------------------
    def to_dataframe(self) -> pd.DataFrame:
        """Ghép điểm danh với thông tin thành viên/sự kiện thành 1 DataFrame."""
        rows = []
        for r in self._attendance:
            member = self._members[r.member_id]
            event = self._events[r.event_id]
            rows.append(
                {
                    "member_id": member.member_id,
                    "member_name": member.full_name,
                    "role": member.get_role_label(),
                    "event_id": event.event_id,
                    "event_name": event.name,
                    "event_category": event.category,
                    "attendance_weight": event.get_attendance_weight(),
                    "checkin_time": r.checkin_time,
                }
            )
        return pd.DataFrame(rows)

    # -- Tỉ lệ tham gia (theo đề bài) ----------------------------------------
    def participation_rate_by_event(self) -> pd.DataFrame:
        """Tỉ lệ tham gia = số người điểm danh / tổng số thành viên."""
        total_members = len(self._members)
        df = self.to_dataframe()
        summary = (
            df.groupby(["event_id", "event_name"])["member_id"]
            .nunique()
            .reset_index(name="attendee_count")
        )
        summary["total_members"] = total_members
        summary["participation_rate"] = (
            summary["attendee_count"] / total_members if total_members else 0
        )
        return summary

    def participation_rate_by_member(self) -> pd.DataFrame:
        """Tỉ lệ tham gia = số sự kiện đã điểm danh / tổng số sự kiện."""
        total_events = len(self._events)
        df = self.to_dataframe()
        summary = (
            df.groupby(["member_id", "member_name", "role"])["event_id"]
            .nunique()
            .reset_index(name="attended_count")
        )
        summary["total_events"] = total_events
        summary["participation_rate"] = (
            summary["attended_count"] / total_events if total_events else 0
        )
        return summary

    # -- Điểm tích cực (nơi đa hình được dùng thật) --------------------------
    def engagement_ranking(self, top_n: int | None = None) -> pd.DataFrame:
        """Xếp hạng thành viên tích cực bằng điểm có trọng số đa hình:

        engagement_score = tổng(trọng số các sự kiện đã tham gia)
                            * hệ số nhân của thành viên
        """
        df = self.to_dataframe()
        weighted = (
            df.groupby(["member_id", "member_name", "role"])["attendance_weight"]
            .sum()
            .reset_index(name="weighted_attendance")
        )
        weighted["score_multiplier"] = weighted["member_id"].map(
            lambda mid: self._members[mid].get_score_multiplier()
        )
        weighted["engagement_score"] = (
            weighted["weighted_attendance"] * weighted["score_multiplier"]
        )
        weighted = weighted.sort_values("engagement_score", ascending=False)
        return weighted.head(top_n) if top_n else weighted

    def member_growth_over_time(self) -> pd.DataFrame:
        """Số lượng thành viên tích lũy theo thời gian (theo join_date)."""
        rows = sorted(
            ({"join_date": m.join_date} for m in self._members.values()),
            key=lambda r: r["join_date"],
        )
        df = pd.DataFrame(rows)
        df["cumulative_members"] = range(1, len(df) + 1)
        return df