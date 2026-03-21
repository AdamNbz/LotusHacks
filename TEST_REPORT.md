# Báo Cáo Kết Quả Kiểm Thử AI Agent - LotusHacks

Tài liệu này tổng hợp kết quả chạy test suite toàn diện cho hệ thống AI Agent (Triage & Coverage) trên branch `features/ai-agent`.

---

## 1. Môi Trường Kiểm Thử

- **OS:** Ubuntu 22.04 (Docker host)

- **Python:** 3.11.0

- **Model LLM:** `gpt-4.1-mini`

- **Embedding Model:** `all-MiniLM-L6-v2` (ChromaDB Native ONNX)

- **Database:** MongoDB (Auth) + ChromaDB (Vector)

- **Framework:** FastAPI

---

## 2. Kết Quả Kiểm Thử Hệ Thống (System Checks)

| Hạng mục | Trạng thái | Ghi chú |
| --- | --- | --- |
| Cấu trúc thư mục & file | **PASS** | Đã tạo đủ các file trong `backend/agent/` |
| Import Modules (9/9) | **PASS** | Đã fix lỗi export `db.py` (`get_db`, `init_db`, `close_db`) |
| FastAPI Health Check | **PASS** | HTTP 200 OK, Version 0.2.0 |
| OpenAPI Docs Generation | **PASS** | Đã sinh thành công 7 endpoints |
| Docker Image Build | **PASS** | Build thành công (Size: 1.3GB) |
| Docker Container Run | **PASS** | Container khởi động và load config, RAG thành công |

---

## 3. Kết Quả Kiểm Thử RAG (Retrieval-Augmented Generation)

| Hạng mục | Trạng thái | Ghi chú |
| --- | --- | --- |
| Text Splitter | **PASS** | Cắt đoạn văn bản chính xác với overlap |
| Indexing Policies | **PASS** | Đã index thành công 9 chunks từ 2 file luật (Bảo Việt, PTI) |
| Retrieval - Query 1 (Phức tạp) | **PASS** | Tìm đúng `Điều 8` về tai nạn phức tạp |
| Retrieval - Query 2 (Coverage) | **PASS** | Tìm đúng điều khoản `loại trừ / bồi thường` |
| Retrieval - Query 3 (Ngập nước) | **PASS** | Tìm đúng điều khoản liên quan `thiên tai / ngập nước` |

---

## 4. Kết Quả Kiểm Thử AI Agent Workflow (5 Test Cases)

Script `test_all_cases.sh` đã chạy 5 kịch bản (Incidents) giả lập thực tế qua API `POST /api/v1/agent/workflow/process-incident`.

### Test Case 1: Tai nạn liên hoàn 3 xe (INC-001)

- **Input:** Tai nạn trên cao tốc, có bên thứ 3, xe không chạy được, có người bị thương.

- **Expected:** `is_complex = TRUE` $\rightarrow$ Assisted Mode.

- **Actual:** **PASS**. Agent 1 nhận diện đúng sự cố phức tạp do có người bị thương và liên quan bên thứ 3 (dẫn chiếu Điều 8).

### Test Case 2: Trầy xước nhẹ tự gây (INC-002)

- **Input:** Trầy xước khi đỗ xe, không bên thứ 3, xe chạy bình thường.

- **Expected:** `is_complex = FALSE`, `is_eligible = FALSE`.

- **Actual:** **PASS**.
  - Agent 1: Đánh giá sự cố đơn giản (không thương tích, không bên thứ 3).
  - Agent 2: Từ chối bồi thường (PTI) do không phải va chạm với xe khác/vật cố định.

### Test Case 3: Ngập nước thủy kích (INC-003)

- **Input:** Xe ngập nước, động cơ thủy kích, không khởi động được.

- **Expected:** Phân loại đúng mức độ nghiêm trọng.

- **Actual:** **PASS**. Agent 1 phân loại là **PHỨC TẠP** (xe không thể di chuyển, cần cứu hộ) $\rightarrow$ Chuyển Assisted Mode.

### Test Case 4: Mất trộm gương chiếu hậu (INC-004)

- **Input:** Mất trộm bộ phận trong bãi đỗ xe.

- **Expected:** Đơn giản $\rightarrow$ Kiểm tra coverage.

- **Actual:** **PASS**.
  - Agent 1: Đánh giá đơn giản.
  - Agent 2: Từ chối bồi thường (Bảo Việt) do chỉ bảo hiểm mất cắp toàn bộ xe, không bảo hiểm mất cắp bộ phận.

### Test Case 5: Va chạm nhẹ với xe máy (INC-005)

- **Input:** Va chạm xe máy, có bên thứ 3, người đi xe máy xây xát nhẹ.

- **Expected:** `is_complex = TRUE`.

- **Actual:** **PASS**. Agent 1 nhận diện đúng sự cố phức tạp do có thương tích (dù nhẹ) và có liên quan đến bên thứ 3.

---

## 5. Kết Luận Chung

- **Tổng số Test Cases API:** 7/7 **PASSED** (bao gồm 5 Incidents, 1 Invalid Input 422, 1 Index API).

- Hệ thống hoạt động **ổn định, chính xác**.

- Luồng phân loại (Triage) và kiểm tra điều kiện (Coverage) phản hồi đúng logic dựa trên bộ luật RAG đã nạp.

- Docker build hoàn chỉnh, sẵn sàng để deploy lên server hoặc chạy local qua `docker-compose`.

*Tài liệu được tạo tự động bởi LotusHacks AI Team.*

