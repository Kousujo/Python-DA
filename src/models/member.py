"""Member và Officer — lớp mô tả thành viên câu lạc bộ.

Officer kế thừa Member và override get_score_multiplier() để cộng thêm
hệ số điểm tích cực cho thành viên ban chủ nhiệm — đây là điểm đa hình
chính mà Club sẽ dùng khi xếp hạng thành viên tích cực.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Member:
    """Thành viên thông thường của câu lạc bộ."""

    member_id: str
    full_name: str
    class_name: str
    join_date: date

    def get_score_multiplier(self) -> float:
        """Hệ số nhân điểm tích cực. Thành viên thường = 1.0."""
        return 1.0

    def get_role_label(self) -> str:
        """Nhãn vai trò hiển thị trong báo cáo/biểu đồ."""
        return "Thành viên"


@dataclass
class Officer(Member):
    """Thành viên ban chủ nhiệm. Có thêm vị trí phụ trách."""

    position: str = field(default="Ban chủ nhiệm")

    def get_score_multiplier(self) -> float:
        """Override: cộng thêm 20% điểm tích cực do đảm nhiệm vai trò quản lý."""
        return 1.2

    def get_role_label(self) -> str:
        return f"Ban chủ nhiệm ({self.position})"