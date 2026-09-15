# Day04 — Prompt Engineering & Tool Calling

**Làm nhóm · K4 Level 3B · Trợ lý AI theo lĩnh vực tự chọn.** Mỗi thành viên tự nộp cùng URL repo nhóm trên VLearn. Repo bài nộp dùng tên `K4-L3-DAY04-HoVaTen-MSSV-PromptEngineeringToolCalling`; khai báo thành viên và đóng góp trong [TEAM.md](TEAM.md).

## Bài lab này làm gì?

Nhóm nhận starter IT Helpdesk có agent loop, tool và dữ liệu công ty **giả lập**, làm mẫu để xây trợ lý cho lĩnh vực tự chọn. Trợ lý cần hiểu yêu cầu như kiểm tra email/VPN, xem tình trạng một máy, tìm hướng dẫn nội bộ, hoặc tạo ticket sau khi đã được xác nhận.

Starter chạy được nhưng hành vi chưa hoàn chỉnh: có thể chọn nhầm tool, điền sai thông tin, không theo kịp hội thoại nhiều lượt hoặc vượt ranh giới an toàn. Nhóm dùng kết quả chạy thật để cải thiện hành vi đó. Đây không phải bài viết lại toàn bộ ứng dụng hay chỉ làm câu trả lời nghe tự nhiên hơn.

Kết quả cần đạt là một agent có thể chọn đúng tool, gửi đúng input, hỏi lại khi thiếu thông tin, tôn trọng sửa/hủy ở lượt sau và không đưa dữ liệu nội bộ ra ngoài.

## Tự chọn lĩnh vực

**IT Helpdesk là format mẫu, không giới hạn đề tài.** Nhóm có thể làm trợ lý bán hàng, du lịch, học tập, thư viện hoặc lĩnh vực khác. Chốt một nhiệm vụ chính, người dùng và luồng công cụ trong báo cáo ngay từ đầu; dùng dữ liệu giả lập. Có thể tái sử dụng agent loop/provider và thay công cụ, dữ liệu theo đề tài.

- Dùng Helpdesk: giữ các bộ kiểm tra IT có sẵn.
- Đổi lĩnh vực: giữ bộ IT gốc để tham khảo; tạo bộ riêng gồm **30 câu cơ bản (20 một lượt + 10 nhiều lượt)** và **12 câu an toàn**, có đầu ra kỳ vọng. Chốt bộ trước v0 và giữ nguyên qua v1–v3. Ghi đường dẫn và lệnh chạy với `--eval-cases` trong report.
- Mọi nhóm đều viết thêm **10 câu mới (5 + 5)**, làm UI, lưu hội thoại và báo cáo. Bộ extension IT là tham khảo cho lĩnh vực khác.

**Điểm: 90 phần chung + tối đa 10 mở rộng = 100.** Mở rộng là chức năng mới ngoài luồng cơ bản đã chốt, có kiểm thử và minh chứng; đổi lĩnh vực không tự được bonus. Ví dụ: thư viện thêm gia hạn mượn sách; du lịch thêm tra cứu tình trạng đặt chỗ; bán hàng thêm kiểm tra điều kiện đổi trả.

## Starter đã có và nhóm cần làm

| Starter đã có | Nhóm cần làm |
|---|---|
| Agent loop, CLI chat, adapter cho provider, 9 tool Helpdesk và dữ liệu giả lập | Đọc lỗi từ run v0; không thay đổi bộ case cố định để tăng điểm |
| `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml` | Cải thiện hai artifact bằng giả thuyết và evidence |
| Eval base 30 case, extension 10 case và adversarial 12 case | Chạy v0, v1, v2, v3 cùng điều kiện và ghi version log |
| Mẫu `starter_v0/data/eval_group.json` để trống | Tự viết đúng 10 case: 5 một lượt và 5 nhiều lượt |
| Mẫu report | Lưu run, transcript; làm UI chat hiện tool call/input/kết quả-lỗi/phiên bản; hoàn thiện report và TEAM |

Nhóm được xây hoặc thay công cụ để phục vụ lĩnh vực đã chọn; đây là phần chung. Dùng prompt và mô tả công cụ để cải thiện hành vi qua v0–v3, sửa code khi lỗi nằm trong cách thực thi. Chức năng ngoài luồng cơ bản đã chốt được xét 10 điểm mở rộng; xem [RUBRIC.md](RUBRIC.md).

## Luồng làm bài

1. Cài môi trường, chạy preflight và chạy **v0 khi chưa sửa**.
2. Chọn failure rõ ràng: sai tool, sai input, thiếu thông tin, nhiều lượt, xác nhận/hủy hoặc an toàn dữ liệu.
3. Đặt một giả thuyết, sửa một phần chính của prompt/tool declaration, rồi chạy lại thành v1, v2, v3.
4. So sánh metric và trace cùng bộ case; ghi thay đổi, lý do và đường dẫn run vào `version_log.csv`.
5. Viết case nhóm, chạy safety, hoàn thiện UI, transcript và report.

Một run chỉ dùng làm bằng chứng khi `provider_error_cases == 0` và `measured_cases == total_cases`. Đọc cả tool result/error; routing PASS không tự chứng minh hành động đã thành công.

## Repo bài nộp cần có gì?

Giữ toàn bộ source trong `starter_v0/`, đồng thời commit evidence thật của nhóm:

| Phần | Bằng chứng tối thiểu |
|---|---|
| Prompt và tool declaration | Bản cuối của `artifacts/system_prompt.md` và `artifacts/tools.yaml` khớp với tool registry |
| Thử nghiệm v0–v3 | Run JSON, `version_log.csv`, giả thuyết và so sánh trước/sau |
| Team eval và safety | `data/eval_group.json` đủ 5+5 case; run adversarial và phân tích ít nhất 3 case |
| UI và transcript | Chat chạy được, cho thấy tool, input, kết quả/lỗi, version và các hội thoại yêu cầu |
| Báo cáo và teamwork | `artifacts/REPORT.md`, [TEAM.md](TEAM.md), commit kỹ thuật và mục INDIVIDUAL của từng người |

Không commit `.env`, API key, dữ liệu thật, `.venv`, cache hoặc ticket phát sinh. Tên repo, cấu trúc nộp và checklist đầy đủ nằm ở [SUBMISSION.md](SUBMISSION.md).

## Chuẩn bị và bắt đầu

Cần Python 3.10+, Git/GitHub và API key của một provider hỗ trợ tool calling. Chỉ cần `TAVILY_API_KEY` nếu nhóm dùng tìm kiếm thông tin thiết bị trên web.

```powershell
cd starter_v0
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Điền **một** key provider vào `.env`, sau đó chạy bản gốc trước khi sửa artifact:

```powershell
python scripts/preflight_provider.py --provider openrouter
python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json
```

Thay `openrouter` bằng `openai`, `anthropic` hoặc `gemini` khi dùng provider khác. Không commit `.env`.

## Tài liệu cần đọc

| File | Dùng khi |
|---|---|
| [SUBMISSION.md](SUBMISSION.md) | Đặt tên repo, chuẩn bị file và nộp VLearn |
| [RUBRIC.md](RUBRIC.md) | Biết cách chấm và bằng chứng cần có |
| [CHECKPOINTS.md](CHECKPOINTS.md) | Theo mốc thời gian của buổi học |
| [RULES.md](RULES.md) | Dùng AI, làm nhóm, deadline và bảo mật |
| [TEAM.md](TEAM.md) | Ghi thành viên, phần việc và INDIVIDUAL |

## Thời gian

Buổi học: **17:30–21:00**. 17:30–17:40 giới thiệu, 17:40–17:50 Kahoot, 17:50–20:25 làm nhóm, 20:25–21:00 demo. Mốc kiểm tra tại lớp là 20:25; xem [CHECKPOINTS.md](CHECKPOINTS.md).

Hạn mặc định là **23:59 ngày học, Asia/Ho_Chi_Minh (UTC+07:00)**. Xem [SUBMISSION.md](SUBMISSION.md) và [RULES.md](RULES.md) để biết bản chốt và quy định nộp muộn.
