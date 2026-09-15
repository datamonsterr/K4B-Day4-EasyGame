# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: EasyGame
- Người đại diện / MSSV: Nguyễn Đức Tâm / 2A202602921
- Tên repo: `K4-L3B-Day04-EasyGame`
- URL repo, nhánh nộp, commit chốt: https://github.com/tamnd2004/K4B-Day-4-Whatever
- Deadline áp dụng và link thông báo đổi hạn nếu có:

## Thành viên

| Họ và tên       | MSSV        | GitHub         | Vai trò và công việc | File/commit/PR |
| --------------- | ----------- | -------------- | -------------------- | -------------- |
| Nguyễn Đức Tâm  | 2A202602921 | tamnd2004      |                      |                |
| Đậu Quang Ý     | 2A202602661 | quangy1007     | Thiết kế & cài đặt bộ 10 test case nhóm (5 single-turn + 5 multi-turn) | starter_v0/data/eval_group.json |
| Nguyễn Tiến Đạt | 2A202602970 | DatTienNguyenn |                      |                |
| Trần Mạnh Hùng  | 2A202602708 | manhhungtr211  |                      |                |
| Phạm Thành Đạt  | 2A202602721 | datamonsterr |                      |                |

## Nhận xét chung

- Kết quả và bằng chứng:
- Thay đổi hiệu quả nhất:
- Giới hạn còn lại:
- Cách phân công và tích hợp:

## INDIVIDUAL

Sao chép mục này cho từng thành viên.

### Nguyễn Đức Tâm — 2A202602921

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:

### Đậu Quang Ý — 2A202602661

- Phần việc và file/commit/PR: Thiết kế và cài đặt toàn bộ 10 test case nguyên bản của nhóm trong `starter_v0/data/eval_group.json` (5 single-turn và 5 multi-turn); kiểm thử tính hợp lệ cú pháp và tính tương thích với registry công cụ.
- Quyết định, khó khăn và cách xử lý: Khó khăn lớn nhất là bao quát đủ các loại lỗi (`wrong_tool`, `wrong_arg_value`, `wrong_boundary`, `unnecessary_tool`, `out_of_scope`, `missing_info`) trong ngữ cảnh thực tế của IT Helpdesk mà không trùng lặp bộ eval base. Đã xây dựng các kịch bản thực tế (kiểm tra máy in mạng, tra cứu nhân viên mới, hủy tạo ticket ở lượt sau, duy trì ngữ cảnh môi trường staging) và dùng script kiểm thử xác thực cấu trúc trước khi tích hợp.
- Điều đã học: Hiểu rõ cơ chế đánh giá tự động (evaluation benchmark) cho các hệ thống LLM Tool Calling, quy chuẩn phân loại lỗi định tuyến công cụ, và sự khác biệt về xử lý ngữ cảnh giữa hội thoại 1 lượt và nhiều lượt.
- AI/công cụ đã dùng và cách kiểm tra: Sử dụng Antigravity và viết script Python kiểm thử để xác thực cấu trúc JSON theo đúng schema quy định và đảm bảo khớp 100% với registry công cụ của bài lab.
- Thời điểm đã tự nộp URL repo chung trên VLearn: [Nộp URL repo trước 23:59]

### Nguyễn Tiến Đạt — 2A202602970

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:

### Trần Mạnh Hùng — 2A202602708

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:

### Phạm Thành Đạt — 2A202602721

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý: model liên tục bị provider error do giới hạn RPM. Xử lý bằng cách thêm cơ chế retry khi gặp lỗi.
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:

## Reconstruction / phân công bản EasyGame

Bản này được chuẩn bị với AI theo phân công của người yêu cầu. Author và ngày Git là metadata tái dựng; xem `docs/provenance.json`. Thời gian run là thời gian thực. Những reflection ở trên được giữ từ repo gốc, không xác nhận lại việc nộp VLearn. Thành viên cần tự review reflection và chạy README; chưa có bằng chứng xác nhận của thành viên trong phiên này.

| GitHub từ TEAM gốc | Alias theo yêu cầu | Phần việc bản EasyGame |
|---|---|---|
| manhhungtr211 | manhhungtr211 | Baseline, môi trường, log, tích hợp và kiểm tra khởi động |
| DatTienNguyenn | DatTienNguyen | v1 routing/clarification, v2 context/confirmation |
| datamonsterr | PhamThanhDat / datamonsterr | v3 safety, vòng sửa tiếp theo, UI Streamlit |
| quangy1007 | quangy | 10 case nhóm gốc và run đối chiếu |
| tamnd2004 | tamnd2004 | 12 safety cases, phân tích trace và REPORT |
