# Tài Liệu Thiết Kế & Triển Khai AI Services - LotusHacks

Tài liệu này mô tả chi tiết kiến trúc, luồng xử lý (workflow) và cách triển khai hệ thống AI Agent phục vụ quy trình tự động hóa bồi thường bảo hiểm ô tô tại Việt Nam.

---

## 1. Tổng Quan Hệ Thống

Hệ thống được thiết kế theo mô hình **Multi-Agent Workflow** kết hợp với công nghệ **RAG (Retrieval-Augmented Generation)**. Mục tiêu là tự động hóa quá trình tiếp nhận sự cố, phân loại mức độ phức tạp, và kiểm tra điều kiện bồi thường sơ bộ dựa trên các bộ luật và điều khoản bảo hiểm.

Hệ thống bao gồm 2 Agent chính:
- **Agent 1 (Triage / Policy Agent)**: Chịu trách nhiệm phân loại sự cố (Phức tạp / Không phức tạp) ngay khi tiếp nhận thông tin.
- **Agent 2 (Coverage Agent)**: Chịu trách nhiệm kiểm tra sơ bộ xem sự cố có nằm trong phạm vi bảo hiểm và có bị loại trừ hay không (chỉ áp dụng cho các ca không phức tạp).

---

## 2. Chi Tiết Các AI Agent

### 2.1. Agent 1: Triage & Policy Engine

**Mục tiêu:** Nhanh chóng xác định mức độ nghiêm trọng của sự cố để đưa ra hướng xử lý khẩn cấp (Assisted Mode) hoặc tiếp tục quy trình tự động (AI Claim Flow).

- **Input:** Thông tin sự cố thu thập từ người dùng (thời gian, địa điểm, mô tả, có bên thứ ba không, xe còn chạy được không, có người bị thương không).
- **Quy trình xử lý (RAG + LLM):**
  1. Hệ thống tạo truy vấn tìm kiếm dựa trên input của người dùng.
  2. RAG truy xuất các điều khoản liên quan từ cơ sở dữ liệu luật bảo hiểm (ChromaDB).
  3. LLM đối chiếu thông tin sự cố với các tiêu chí phân loại "Phức tạp" (ví dụ: có người bị thương, tai nạn liên hoàn, liên quan bên thứ 3, xe không thể di chuyển).
- **Output:** JSON chứa 2 trường:
  - `is_complex` (boolean): `true` nếu phức tạp, `false` nếu đơn giản.
  - `description` (string): Giải thích chi tiết lý do dựa trên điều khoản cụ thể.
- **Hành động tiếp theo:**
  - Nếu `is_complex == true`: Chuyển sang **Assisted Mode** (Cung cấp hotline khẩn cấp, hướng dẫn giữ hiện trường, gọi công an/cấp cứu). Workflow dừng tại đây.
  - Nếu `is_complex == false`: Chuyển tiếp thông tin cho Agent 2.

### 2.2. Agent 2: Coverage Pre-check

**Mục tiêu:** Kiểm tra xem sự cố có đủ điều kiện để được bồi thường theo hợp đồng bảo hiểm hay không, từ đó sinh ra danh sách hồ sơ cần thiết hoặc cảnh báo từ chối.

- **Input:** Thông tin sự cố từ người dùng + Tên nhà bảo hiểm (Insurer).
- **Quy trình xử lý (RAG + LLM):**
  1. Hệ thống tạo truy vấn tìm kiếm tập trung vào "Phạm vi bảo hiểm" và "Điểm loại trừ" của nhà bảo hiểm tương ứng.
  2. RAG truy xuất các điều khoản bồi thường chi tiết từ ChromaDB.
  3. LLM phân tích xem sự cố có nằm trong phạm vi bảo hiểm không, hoặc có vi phạm điểm loại trừ nào không (ví dụ: hao mòn tự nhiên, tự ý gây trầy xước không do tai nạn).
- **Output:** JSON chứa 2 trường:
  - `is_eligible` (boolean): `true` nếu đủ điều kiện sơ bộ, `false` nếu nguy cơ bị từ chối cao.
  - `description` (string): Giải thích chi tiết phạm vi áp dụng và điểm loại trừ.
- **Hành động tiếp theo:**
  - Nếu `is_eligible == true`: Đủ điều kiện $\rightarrow$ Sinh checklist hồ sơ động theo yêu cầu của nhà bảo hiểm.
  - Nếu `is_eligible == false`: Cảnh báo nguy cơ bị từ chối $\rightarrow$ Gợi ý người dùng tự sửa chữa ngoài hoặc chỉ lưu hồ sơ nháp.

---

## 3. Kiến Trúc RAG (Retrieval-Augmented Generation)

Hệ thống RAG được thiết kế tối ưu để chạy mượt mà trên môi trường không có GPU mạnh (như yêu cầu của dự án).

### 3.1. Vector Database
- **Công nghệ:** `ChromaDB` (chạy local, lưu trữ persistent tại thư mục `backend/agent/app/data/chroma_db`).
- **Embedding Model:** Sử dụng default embedding function của ChromaDB (`all-MiniLM-L6-v2` ONNX). Model này nhẹ, chạy hoàn toàn bằng CPU, không cần gọi API bên ngoài, tiết kiệm chi phí và tăng tốc độ xử lý.

### 3.2. Quy Trình Indexing (Chuẩn bị dữ liệu)
1. Dữ liệu luật bảo hiểm (các file `.txt` trong `app/data/`) được đọc và làm sạch.
2. Text được chia nhỏ (chunking) bằng `RecursiveCharacterTextSplitter` với kích thước `chunk_size=800` và `chunk_overlap=150` để giữ nguyên ngữ cảnh của các điều khoản luật.
3. Các chunks được mã hóa (embedding) và lưu vào ChromaDB.

### 3.3. Quy Trình Retrieval (Truy xuất)
1. Khi có request, query của người dùng được mã hóa.
2. ChromaDB thực hiện Semantic Search (Cosine Similarity) để tìm ra top 5 chunks liên quan nhất.
3. Các chunks này được ghép lại thành context và nhúng vào prompt gửi cho LLM.

---

## 4. Công Nghệ Sử Dụng (Tech Stack)

| Thành phần | Công nghệ | Lý do lựa chọn |
| :--- | :--- | :--- |
| **Backend Framework** | FastAPI (Python 3.11) | Hiệu năng cao, hỗ trợ Async/Await, tự động sinh OpenAPI docs. |
| **LLM Orchestration** | LangChain / OpenAI API | Dễ dàng quản lý prompt, tích hợp linh hoạt với nhiều model (GPT, Qwen). |
| **Vector Database** | ChromaDB | Mã nguồn mở, nhẹ, chạy local không cần cài đặt server phức tạp. |
| **Embedding Model** | `all-MiniLM-L6-v2` (ONNX) | Chạy CPU cực nhanh, không phụ thuộc API key, độ chính xác tốt cho RAG. |
| **Database (Auth)** | MongoDB | Lưu trữ thông tin user, linh hoạt cho schema không cấu trúc. |
| **Containerization** | Docker & Docker Compose | Đóng gói toàn bộ môi trường, đảm bảo chạy ổn định trên mọi máy (kể cả Windows HP). |

---

## 5. Hướng Dẫn Triển Khai & Cài Đặt

Toàn bộ dịch vụ AI Agent đã được đóng gói bằng Docker, giúp bạn dễ dàng chạy trên máy tính Windows mà không cần cài đặt môi trường Python phức tạp.

### 5.1. Yêu cầu hệ thống
- Đã cài đặt **Docker Desktop** trên Windows.
- Đã clone repository về máy.

### 5.2. Cấu hình biến môi trường
1. Tại thư mục gốc của dự án, copy file `.env.example` thành `.env`:
   ```bash
   cp .env.example .env
   ```
2. Mở file `.env` và điền `OPENAI_API_KEY`. (Hệ thống hỗ trợ model `gpt-4o-mini` hoặc các model OpenAI-compatible khác).

### 5.3. Khởi động hệ thống
Chạy lệnh sau tại thư mục gốc của dự án:
```bash
docker-compose up --build -d
```
Lệnh này sẽ khởi động 2 container:
- `lotushacks-mongo`: Database MongoDB.
- `lotushacks-backend-agent`: Dịch vụ FastAPI chứa AI Agent (chạy tại port `8000`).

### 5.4. Chuẩn bị dữ liệu RAG (Chỉ chạy lần đầu)
Sau khi container chạy lên, bạn cần index dữ liệu luật bảo hiểm vào ChromaDB.
Chạy lệnh sau:
```bash
docker exec -it lotushacks-backend-agent python -m app.rag.index_policies
```
*Kết quả mong đợi: Hệ thống báo đã index thành công các chunks vào ChromaDB.*

---

## 6. Tài Liệu API (Endpoints)

Sau khi khởi động, bạn có thể truy cập Swagger UI tại: `http://localhost:8000/docs`

### 6.1. Xử lý sự cố (Main Workflow)
- **Endpoint:** `POST /api/v1/agent/workflow/process-incident`
- **Chức năng:** Gửi thông tin sự cố qua pipeline 2 Agent.
- **Payload mẫu:**
  ```json
  {
    "time": "2024-06-15 08:30",
    "location": "Cao tốc TP.HCM",
    "description": "Va chạm liên hoàn 3 xe",
    "incident_type": "va_cham",
    "third_party_involved": true,
    "vehicle_drivable": false,
    "injuries": true,
    "insurer": "Bảo Việt"
  }
  ```

### 6.2. Kiểm tra trạng thái RAG
- **Endpoint:** `GET /api/v1/agent/workflow/rag-stats`
- **Chức năng:** Trả về số lượng chunks luật đã được index trong database.

### 6.3. Trigger Index lại luật
- **Endpoint:** `POST /api/v1/agent/workflow/index-policies`
- **Chức năng:** Dùng khi bạn thêm file `.txt` luật mới vào thư mục `backend/agent/app/data/` và muốn hệ thống cập nhật.

---

## 7. Dữ Liệu Dummy Đã Chuẩn Bị

Hệ thống đã được tích hợp sẵn các dữ liệu để bạn test ngay lập tức:
1. **Luật bảo hiểm (Policy):**
   - `policy_baoviet.txt`: Mẫu điều khoản đơn giản hóa của Bảo Việt.
   - `policy_pti.txt`: Mẫu điều khoản đơn giản hóa của PTI.
2. **Ca kiểm thử (Test Cases):** Nằm tại `backend/agent/app/data/dummy_incidents.json` bao gồm 5 ca:
   - Ca 1: Tai nạn liên hoàn, có thương tích (Sẽ bị Agent 1 chặn lại báo Phức tạp).
   - Ca 2: Trầy xước nhẹ tự gây (Agent 1 báo Đơn giản $\rightarrow$ Agent 2 báo Không đủ điều kiện bồi thường).
   - Ca 3: Ngập nước thủy kích.
   - Ca 4: Mất cắp bộ phận.
   - Ca 5: Va chạm nhẹ với xe máy.

---
*Tài liệu được tạo tự động bởi LotusHacks AI Team.*
