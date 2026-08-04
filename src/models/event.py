"""Event, MandatoryEvent, OptionalEvent — lớp mô tả sự kiện của câu lạc bộ.

MandatoryEvent / OptionalEvent override get_attendance_weight() để quy
định trọng số điểm danh khác nhau — điểm đa hình thứ hai, dùng khi Club
tính tỉ lệ tham gia/điểm tích cực có trọng số.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class Event:
    """Sự kiện cơ bản của câu lạc bộ (lớp cơ sở)."""

    event_id: str
    name: str
    date: date
    category: str

    def get_attendance_weight(self) -> float:
        """Trọng số điểm danh dùng khi tính điểm tích cực. Mặc định = 1.0."""
        return 1.0


@dataclass
class MandatoryEvent(Event):
    """Sự kiện bắt buộc — trọng số điểm danh cao hơn sự kiện tự chọn."""

    def get_attendance_weight(self) -> float:
        return 1.5


@dataclass
class OptionalEvent(Event):
    """Sự kiện tự chọn — trọng số điểm danh thấp hơn sự kiện bắt buộc."""

    def get_attendance_weight(self) -> float:
        return 0.8