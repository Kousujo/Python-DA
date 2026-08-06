"""Sanity check cho src/models/ — chay: python tests/test_club_engagement.py

Khong dung framework/fixture, assert thang. Bat regression khi sua
Member/Event/Club sau nay (da hinh, trong so, exception)."""

import sys
from datetime import date, datetime
from pathlib import Path

# Cho phep import src/ khi chay truc tiep tu thu muc tests/ (sys.path[0]=tests/)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.models.club import Club
from src.models.event import MandatoryEvent, OptionalEvent
from src.models.exceptions import DuplicateAttendanceError, MemberNotFoundError
from src.models.member import Member, Officer

club = Club()
club.add_member(Member("M1", "Thanh vien A", "", date(2025, 1, 1)))
club.add_member(Officer("M2", "Truong ban B", "", date(2025, 1, 1), position="Chu nhiem"))
club.add_event(MandatoryEvent("E1", "Hop bat buoc", date(2025, 2, 1), "Sinh hoat"))
club.add_event(OptionalEvent("E2", "Workshop tu chon", date(2025, 2, 5), "Dao tao"))

club.check_in("M1", "E1", datetime(2025, 2, 1, 8, 0))
club.check_in("M2", "E1", datetime(2025, 2, 1, 8, 0))
club.check_in("M2", "E2", datetime(2025, 2, 5, 8, 0))

assert club._events["E1"].get_attendance_weight() == 1.5
assert club._events["E2"].get_attendance_weight() == 0.8

assert club._members["M1"].get_score_multiplier() == 1.0
assert club._members["M2"].get_score_multiplier() == 1.2

ranking = club.engagement_ranking()
top = ranking.iloc[0]
assert top["member_id"] == "M2"
assert abs(top["engagement_score"] - (1.5 + 0.8) * 1.2) < 1e-9

try:
    club.check_in("M999", "E1", datetime.now())
    raise AssertionError("Phai nem MemberNotFoundError")
except MemberNotFoundError:
    pass

try:
    club.check_in("M1", "E1", datetime.now())
    raise AssertionError("Phai nem DuplicateAttendanceError")
except DuplicateAttendanceError:
    pass

print("OK - tat ca assert pass (da hinh + exception dung dac ta).")