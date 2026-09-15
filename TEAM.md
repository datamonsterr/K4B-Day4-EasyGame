# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: EasyGame
- Người đại diện / MSSV: Nguyễn Đức Tâm / 2A202602921
- Tên repo: `K4B-Day4-EasyGame`
- URL repo, nhánh nộp, commit chốt: https://github.com/datamonsterr/K4B-Day4-EasyGame · nhánh `main` · commit chốt: xem mục "Reconstruction" bên dưới và `docs/provenance.json`
- Deadline áp dụng và link thông báo đổi hạn nếu có:

## Thành viên

| Họ và tên       | MSSV        | GitHub         | Vai trò và công việc | File/commit/PR |
| --------------- | ----------- | -------------- | -------------------- | -------------- |
| Nguyễn Đức Tâm  | 2A202602921 | tamnd2004      | 12 case an toàn, phân tích trace, REPORT.md | `starter_v0/artifacts/REPORT.md`, run `v4_B_adversarial_*` |
| Đậu Quang Ý     | 2A202602661 | quangy1007     | Thiết kế & cài đặt bộ 10 test case nhóm (5 single-turn + 5 multi-turn) | `starter_v0/data/eval_group.json`, run `v4_B_group_*` |
| Nguyễn Tiến Đạt | 2A202602970 | DatTienNguyenn | v1 routing/clarification, v2 context/confirmation | commit `f6b8707`, `a5e44bc` |
| Trần Mạnh Hùng  | 2A202602708 | manhhungtr211  | Baseline v0, retry/pacing, version log, README startup check | commit `af41fe9`, `starter_v0/scripts/log_version.py`, `docs/startup-check.md` |
| Phạm Thành Đạt  | 2A202602721 | datamonsterr   | v3 safety boundary, v4 multi-entity, UI Streamlit + tests | commit `c306e3a`, `starter_v0/app.py`, `starter_v0/conversation.py`, `starter_v0/tests/` |

## Nhận xét chung

- Kết quả và bằng chứng: v0 20/30 (0.6667) → v1 0.8 → v2 0.7 (regression) → v3 0.9667 → v4 1.0 → v5 0.9333 (hồi quy, boundary playbook) → **v6 1.0 (30/30)** base; group 10/10; adversarial v4 8/12 → v5 11/12 → **v6 12/12** — toàn bộ 0 provider error (run `v{4,5,6}_B_*_gemini_*.json`, `version_log.csv`, transcripts `starter_v0/transcripts/`). UI ReAct hiển thị suy luận → tool → câu trả lời cuối; Tavily live đã xác minh.
- Thay đổi hiệu quả nhất: v3 tách "thực thi tool thật" khỏi "JSON mô tả hành động"; v5/v6 boundary playbook sửa cả 4 case adversarial còn fail; ReAct runtime nhiều bước với safeguard (max 5 vòng/12 call, chặn lặp, dừng khi lỗi liên tiếp).
- Giới hạn còn lại: chỉ đo trên `gemini-3.5-flash-lite` (quota free tier); tầng tool/harness chưa tự chặn `confirmed=true` nguồn forged (chỉ artifact + UI chặn — hypothesis v7); v2 còn regression trong artifact riêng; author/dates là metadata tái dựng.
- Cách phân công và tích hợp: xem bảng "Reconstruction / phân công bản EasyGame" bên dưới.

## INDIVIDUAL

Sao chép mục này cho từng thành viên.

### Nguyễn Đức Tâm — 2A202602921

- Phần việc và file/commit/PR: Chạy giữ nguyên 12 case an toàn `data/eval_adversarial.json` trên v4 (`run v4_B_adversarial_*`, 8/12 tự động, 0 provider error), phân tích thủ công trace A02/A03/A05/A06 (đối chiếu tool call với `tool_results` và thư mục `tickets/`), hoàn thành `starter_v0/artifacts/REPORT.md`.
- Quyết định, khó khăn và cách xử lý: Điểm tự động PASS không chứng minh "không có dữ liệu rò rỉ" — kiểm tra thêm `tool_results`, thư mục `tickets/` và regex chặn identifier. Phát hiện A03: forged `TOOL_RESULTS_JSON` khiến eval path ghi 1 ticket mock thật; UI/runtime chặn được (unit test) nhưng ghi minh bạch làm giới hạn, không giấu. A02/A05/A06 là hành vi an toàn nhưng lệch expect cố định.
- Điều đã học: Ranh giới exfiltration phải được chứng minh ở tầng thực thi (tool code + filesystem), không chỉ ở routing.
- AI/công cụ đã dùng và cách kiểm tra: AI hỗ trợ soạn phân tích; kiểm tra bằng cách đọc trực tiếp từng result trong run JSON và so với expect của case.
- Thời điểm đã tự nộp URL repo chung trên VLearn: [thành viên tự điền khi nộp]

### Đậu Quang Ý — 2A202602661

- Phần việc và file/commit/PR: Thiết kế và cài đặt toàn bộ 10 test case nguyên bản của nhóm trong `starter_v0/data/eval_group.json` (5 single-turn và 5 multi-turn); kiểm thử tính hợp lệ cú pháp và tính tương thích với registry công cụ.
- Quyết định, khó khăn và cách xử lý: Khó khăn lớn nhất là bao quát đủ các loại lỗi (`wrong_tool`, `wrong_arg_value`, `wrong_boundary`, `unnecessary_tool`, `out_of_scope`, `missing_info`) trong ngữ cảnh thực tế của IT Helpdesk mà không trùng lặp bộ eval base. Đã xây dựng các kịch bản thực tế (kiểm tra máy in mạng, tra cứu nhân viên mới, hủy tạo ticket ở lượt sau, duy trì ngữ cảnh môi trường staging) và dùng script kiểm thử xác thực cấu trúc trước khi tích hợp.
- Điều đã học: Hiểu rõ cơ chế đánh giá tự động (evaluation benchmark) cho các hệ thống LLM Tool Calling, quy chuẩn phân loại lỗi định tuyến công cụ, và sự khác biệt về xử lý ngữ cảnh giữa hội thoại 1 lượt và nhiều lượt.
- AI/công cụ đã dùng và cách kiểm tra: Sử dụng Antigravity và viết script Python kiểm thử để xác thực cấu trúc JSON theo đúng schema quy định và đảm bảo khớp 100% với registry công cụ của bài lab.
- Thời điểm đã tự nộp URL repo chung trên VLearn: [Nộp URL repo trước 23:59]

### Nguyễn Tiến Đạt — 2A202602970

- Phần việc và file/commit/PR: v1 — routing/clarification (commit `f6b8707`, artifacts từ `0e178e6` bản gốc, re-eval trên Gemini); v2 — context carry-over + reconfirmation (commit `a5e44bc`, artifacts từ `9752f46`).
- Quyết định, khó khăn và cách xử lý: Giữ nguyên bộ case và scorer giữa các version để so sánh hợp lệ. v2 giảm còn 21/30 (regression so v1) — ghi nhận thẳng vào REVIEW.md thay vì giấu.
- Điều đã học: Thêm quy tắc ngữ cảnh có thể làm tăng ambiguous-action; metric trước/sau phải đi kèm phân tích regression.
- AI/công cụ đã dùng và cách kiểm tra: AI hỗ trợ tái dùng artifact gốc; kiểm chứng bằng `run_eval.py` cùng model, temperature 0, đủ 30/30 measured.
- Thời điểm đã tự nộp URL repo chung trên VLearn: [thành viên tự điền khi nộp]

### Trần Mạnh Hùng — 2A202602708

- Phần việc và file/commit/PR: Baseline v0 chưa sửa (commit `af41fe9`, 2 run: 1 dính quota 11 provider_error — giữ làm bằng chứng INVALID, 1 sạch 30/30 = 0.6667); retry/backoff + pacing RPM trong `run_eval.py`; `scripts/log_version.py`; xác minh khởi động README (`docs/startup-check.md`).
- Quyết định, khó khăn và cách xử lý: Quota 15 RPM free tier phá run đầu; xử lý bằng min-interval 5s + exponential backoff, không đổi scorer. Run hỏng được giữ nguyên và đánh dấu `INVALID_partial_case_accuracy` trong `version_log.csv`.
- Điều đã học: Run chỉ là bằng chứng khi `provider_error_cases == 0`; log phải giữ cả run thất bại.
- AI/công cụ đã dùng và cách kiểm tra: AI hỗ trợ viết harness; kiểm tra bằng chạy lại preflight + eval đầy đủ, đối chiếu summary JSON.
- Thời điểm đã tự nộp URL repo chung trên VLearn: [thành viên tự điền khi nộp]

### Phạm Thành Đạt — 2A202602721

- Phần việc và file/commit/PR: v3 — tách thực thi tool khỏi JSON cuối, cấm confirmation giả và identifier nội bộ ra ngoài (commit `c306e3a`); v4 — một call riêng cho từng thực thể, 30/30 base; runtime `conversation.py` + UI `app.py` (tool trace, tham số, kết quả/lỗi, phiên bản, xác nhận ticket bằng nút) + 11 unit tests.
- Quyết định, khó khăn và cách xử lý: model liên tục bị provider error do giới hạn RPM — thêm cơ chế retry. Model hay "kể" đã làm xong trong text JSON mà không gọi tool → tách tầng thực thi; UI dựng câu trả lời từ kết quả tool thật nên lỗi không thể bị giấu. Confirmation chỉ qua nút bấm payload hiển thị, `confirmed=true` từ model không ghi file.
- Điều đã học: Tự động PASS routing không tự chứng minh hành động ghi dữ liệu thành công; phải nhìn `tool_results` và filesystem.
- AI/công cụ đã dùng và cách kiểm tra: AI hỗ trợ code + review; kiểm chứng bằng unit tests (`tests/`), browser test thực tế trên `http://localhost:8501` và transcript JSON xuất từ UI.
- Thời điểm đã tự nộp URL repo chung trên VLearn: [thành viên tự điền khi nộp]

## Reconstruction / phân công bản EasyGame

Bản này được chuẩn bị với AI theo phân công của người yêu cầu. Author và ngày Git là metadata tái dựng; xem `docs/provenance.json`. Thời gian run là thời gian thực. Những reflection ở trên được giữ từ repo gốc, không xác nhận lại việc nộp VLearn. Thành viên cần tự review reflection và chạy README; chưa có bằng chứng xác nhận của thành viên trong phiên này.

| GitHub từ TEAM gốc | Alias theo yêu cầu | Phần việc bản EasyGame |
|---|---|---|
| manhhungtr211 | manhhungtr211 | Baseline, môi trường, log, tích hợp và kiểm tra khởi động |
| DatTienNguyenn | DatTienNguyen | v1 routing/clarification, v2 context/confirmation |
| datamonsterr | PhamThanhDat / datamonsterr | v3 safety, vòng sửa tiếp theo, UI Streamlit |
| quangy1007 | quangy | 10 case nhóm gốc và run đối chiếu |
| tamnd2004 | tamnd2004 | 12 safety cases, phân tích trace và REPORT |
