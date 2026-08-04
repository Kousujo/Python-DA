"""Ngoại lệ nghiệp vụ dùng khi thao tác với Club (điểm danh, tra cứu)."""


class ClubManagementError(Exception):
    """Lớp cơ sở cho mọi lỗi nghiệp vụ của hệ thống quản lý câu lạc bộ."""


class MemberNotFoundError(ClubManagementError):
    """Không tìm thấy thành viên với member_id được cung cấp."""

    def __init__(self, member_id: str) -> None:
        super().__init__(f"Không tìm thấy thành viên có mã: {member_id}")
        self.member_id = member_id


class EventNotFoundError(ClubManagementError):
    """Không tìm thấy sự kiện với event_id được cung cấp."""

    def __init__(self, event_id: str) -> None:
        super().__init__(f"Không tìm thấy sự kiện có mã: {event_id}")
        self.event_id = event_id


class DuplicateAttendanceError(ClubManagementError):
    """Thành viên đã được điểm danh cho sự kiện này trước đó."""

    def __init__(self, member_id: str, event_id: str) -> None:
        super().__init__(
            f"Thành viên {member_id} đã được điểm danh cho sự kiện {event_id}"
        )
        self.member_id = member_id
        self.event_id = event_id