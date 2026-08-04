# Project Rule — Hệ thống quản lý câu lạc bộ sinh viên

Quy tắc này dành cho Cline khi thực thi các đặc tả/code được dán từ Claude vào workspace này.

## 0. Vai trò của Cline trong workflow này

Kiến trúc, thiết kế class, và kế hoạch triển khai đã được Claude chốt trước (xem `README.md`). Cline **thực thi theo đúng đặc tả được dán vào**, không tự ý thiết kế lại kiến trúc, không tự đổi tên module/class đã định trong README trừ khi người dùng yêu cầu rõ. Nếu thấy đặc tả được dán có mâu thuẫn với `README.md` hiện tại trong repo, dừng lại và hỏi người dùng trước khi code, không tự suy diễn.

## 1. Quy ước đặt tên & code style

- Định danh (class, function, variable, file, folder) bằng **tiếng Anh**, theo PEP8 (`snake_case` cho function/variable, `PascalCase` cho class).
- Docstring và comment giải thích **nghiệp vụ** (tại sao/ý nghĩa số liệu) viết bằng **tiếng Việt** — vì đây là dự án nộp báo cáo tiếng Việt.
- Type hint đầy đủ cho tham số và giá trị trả về của mọi function/method public.
- Không dùng biến toàn cục ngoài `src/config.py`.
- Không thêm dependency mới vào `requirements.txt` nếu chưa được yêu cầu trong đặc tả dán vào.

## 2. Nguyên tắc thay đổi code

- Ưu tiên thay đổi tối thiểu, đúng phạm vi đặc tả — không viết lại toàn bộ file nếu chỉ cần sửa một phần.
- Không xoá hoặc viết đè logic đã có nếu đặc tả không yêu cầu thay nó.
- Nếu một class/method đã tồn tại và đặc tả mới chỉ bổ sung, hãy mở rộng (thêm method/attribute) — không tạo bản sao trùng chức năng.
- Sau khi thực thi mỗi bước, chạy thử nhanh (import module hoặc chạy 1 lệnh Python nhỏ) để chắc không có lỗi cú pháp/import trước khi báo hoàn thành.

## 3. Xử lý ngoại lệ & dữ liệu

- Mọi bước đọc CSV, truy vấn `Club` theo `member_id`/`event_id` phải bọc `try/except` với exception nghiệp vụ định nghĩa trong `src/models/exceptions.py` — không dùng `except Exception` chung để nuốt lỗi.
- Dữ liệu hiện tại trong `data/raw/` là **dữ liệu mô phỏng placeholder**, sẽ được thay bằng dữ liệu thật từ CLB sau. Vì vậy: không hard-code số liệu cụ thể (tên người, số lượng cụ thể) trong logic xử lý — logic phải hoạt động đúng với bất kỳ dữ liệu nào tuân theo đúng schema cột đã định trong README.

## 4. OOP — điểm bắt buộc giữ nguyên

- Quan hệ kế thừa `Officer(Member)` và `MandatoryEvent(Event)`/`OptionalEvent(Event)` là **bắt buộc phải giữ** — đây là phần chấm điểm CLO4 (30%) của rubric. Không được "làm gọn" bằng cách gộp lại thành 1 class có cờ `is_officer`/`event_type` kiểu string.
- Đa hình phải được **dùng thật** trong `Club` (gọi `.get_attendance_weight()` / `.get_score_multiplier()` qua interface chung), không viết `if isinstance(...)` để rẽ nhánh thay cho override.

## 5. Git

- Commit nhỏ, theo từng phase trong README (mục 6), message ngắn gọn dạng: `feat(models): add Member, Officer with polymorphic score multiplier`.
- Không commit trực tiếp dữ liệu thật của CLB nếu sau này có (kiểm tra `.gitignore` trước khi thêm data thật vào `data/raw/`).

## 6. Khi không chắc

Nếu đặc tả được dán vào không đủ rõ để thực thi (thiếu tên cột, thiếu định nghĩa method), dừng lại và hỏi người dùng — không tự bịa mặc định quan trọng (schema dữ liệu, tên class, công thức tính điểm).
