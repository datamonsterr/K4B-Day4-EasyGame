# K4-L3B-Day04-EasyGame

Trợ lý IT Helpdesk cho **Northstar Labs** (dữ liệu giả lập), dùng **Gemini `gemini-3.5-flash-lite`**. Chat tương tác lưu hội thoại nhiều lượt và hiển thị tool, input, result/error, phiên bản và trạng thái xử lý.

## Mở UI

Từ thư mục repository:

```bash
cd starter_v0
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
# Chỉ cho máy mới; không ghi đè .env đã có:
test -f .env || cp .env.example .env
# Điền GEMINI_API_KEY trong .env
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Mở **http://localhost:8501**. Windows PowerShell: thay lệnh activate bằng `.\.venv\Scripts\Activate.ps1`, và dùng `Copy-Item .env.example .env` nếu chưa có `.env`.

Bản sao `.env` từ repo gốc đã được giữ local và Git ignore. Ứng dụng và mọi run mới dùng Gemini; không đọc biến `MODEL` của OpenRouter. `TAVILY_API_KEY` là tùy chọn; khi thiếu, public web search hiện `missing_api_key` và không tuyên bố đã tìm kiếm thành công.

### Dùng chat và xem evidence

- Chat: nhập yêu cầu; trạng thái “Đang suy nghĩ” hiện trong lúc xử lý. Lịch sử chat cuộn được, khung nhập luôn cố định dưới cùng; tên provider/model hiển thị trong khung nhập. Sidebar thu gọn/mở được, có nút chuyển **💬 Chat** / **📊 Runs & evidence**.
- Mở từng tool để xem input và kết quả/lỗi. Câu trả lời sau tool được dựng từ kết quả thực thi; lỗi tool luôn hiển thị rõ và không bị nói là hoàn thành.
- Ticket: agent có thể hỏi lại trước; khi có payload, bấm **Xác nhận ghi ticket** để ghi file mô phỏng. Tin nhắn mới hoặc hủy làm mất hiệu lực payload chờ. Không có kết nối ticketing production.
- **Hội thoại mới** tạo lịch sử riêng. **Tải transcript JSON** xuất bằng chứng; bản local tự lưu trong `starter_v0/transcripts/`.
- **Runs & evidence** (chuyển qua nút ở sidebar): chọn run và case để đọc câu hỏi, routing/args, tool error và phiên bản. Điểm routing PASS không chứng minh tool thành công.

## Chạy eval

Từ `starter_v0` với venv đã activate:

```bash
python scripts/preflight_provider.py --provider gemini --model gemini-3.5-flash-lite
python run_eval.py --provider gemini --model gemini-3.5-flash-lite --version v4 --suite base --eval-cases data/eval_base.json --min-interval 5 --max-retries 3
python run_eval.py --provider gemini --model gemini-3.5-flash-lite --version v4 --suite adversarial --eval-cases data/eval_adversarial.json --min-interval 5 --max-retries 3
python run_eval.py --provider gemini --model gemini-3.5-flash-lite --version v4 --suite group --eval-cases data/eval_group.json --min-interval 5 --max-retries 3
python -m unittest discover -s tests -v
```

Dùng phiên bản cuối trong `starter_v0/artifacts/CURRENT_VERSION` thay cho `v3` nếu có vòng tiếp theo. Chạy tuần tự để tránh giới hạn RPM. Mỗi run có file mới; giữ cả run lỗi provider, nhưng chỉ dùng metric khi đo đủ mọi case và `provider_error_cases == 0`.

Để chạy lại phiên bản cũ, thêm `--system-prompt artifacts/versions/v1/system_prompt.md --tools artifacts/versions/v1/tools.yaml --version v1`. Bản `v0` giữ prompt/tool gốc; harness đã thêm pacing/retry từ source sau lần chạy đầu bị quota. Baseline đạt hay không được lưu nguyên trạng.

## Kết quả và phân công

- [REPORT: metric, regression, safety và demo](starter_v0/artifacts/REPORT.md)
- [Version log CSV](starter_v0/artifacts/version_log.csv)
- [TEAM và mapping alias](TEAM.md)
- [Nguồn và metadata timeline tái dựng](docs/provenance.json)
- [Kế hoạch](docs/superpowers/plans/2026-09-15-easygame.md)
- [Đề bài gốc](docs/assignment.md)

Author và thời gian commit được phân công/tái dựng theo yêu cầu, bắt đầu 4.5 giờ trước thời điểm chuẩn bị timeline, với khoảng thời gian ước lượng cho từng bước. Đây không phải bằng chứng thành viên tự làm ở các thời điểm đó. Run/transcript dùng thời gian thực. Không khẳng định đã push, nộp VLearn, hay có thành viên khác review khi chưa có evidence.

## Kiểm tra khởi động bởi thành viên khác

Hướng dẫn kiểm tra: làm theo lệnh mở UI, hỏi “VPN production có ổn không?”, mở trace, kiểm tra phiên bản; hỏi “Kiểm tra máy LT-999999” và xác nhận thấy `asset_not_found`; xuất transcript. Ghi tên, thời gian và kết quả vào `docs/startup-check.md`. Kiểm thử tự động của AI không thay thế xác nhận của thành viên.

Tài liệu API UI: [chat input](https://docs.streamlit.io/develop/api-reference/chat/st.chat_input), [status](https://docs.streamlit.io/develop/api-reference/status/st.status), [AppTest](https://docs.streamlit.io/develop/api-reference/app-testing).
