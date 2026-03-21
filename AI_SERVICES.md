# 🤖 Kiến trúc AI Agents - LotusHacks

Tài liệu này mô tả chi tiết về hệ thống AI Agents được tích hợp trong LotusHacks nhằm tự động hóa quy trình bồi thường bảo hiểm ô tô.

## 1. Tổng quan Kiến trúc

Hệ thống sử dụng kiến trúc **Multi-Agent** kết hợp với **RAG (Retrieval-Augmented Generation)** để đảm bảo tính chính xác, dựa trên dữ liệu luật bảo hiểm thực tế, và giảm thiểu rủi ro hallucination (ảo giác) của LLM.

Kiến trúc bao gồm 2 Agent chính chạy tuần tự:

1. **Agent 1 (Triage Agent):** Đóng vai trò như một nhân viên tiếp nhận ban đầu (First Notice of Loss). Nhiệm vụ là đánh giá mức độ nghiêm trọng của sự cố.
2. **Agent 2 (Coverage Agent):** Đóng vai trò như một chuyên viên bồi thường sơ bộ. Nhiệm vụ là đối chiếu sự cố với hợp đồng bảo hiểm để xem có thuộc phạm vi bảo hiểm hay không.

Cả 2 Agent đều được cung cấp Context từ **ChromaDB** (chứa các điều khoản hợp đồng bảo hiểm của Bảo Việt, PTI, v.v.).

---

## 2. Chi tiết Workflow

### Bước 1: Tiếp nhận thông tin (User Input)
Người dùng nhập thông tin sự cố qua giao diện (hoặc API):
- Thời gian, địa điểm
- Mô tả sự cố (text tự do)
- Có bên thứ ba liên quan không?
- Xe còn chạy được không?
- Có người bị thương không?
- Nhà bảo hiểm (VD: Bảo Việt, PTI)

### Bước 2: Agent 1 - Triage (Phân loại)
Agent 1 sẽ phân tích thông tin đầu vào.

- **Tiêu chí "Phức tạp":** Có người bị thương, liên quan bên thứ ba, tai nạn liên hoàn, xe không chạy được, v.v.
- **RAG Context:** Truy xuất các điều khoản liên quan đến "trách nhiệm khi xảy ra sự cố", "giữ nguyên hiện trường".
- **Quyết định:**
  - Nếu **PHỨC TẠP** (is_complex = true): Hệ thống dừng lại, chuyển sang chế độ **Assisted Mode**. Gợi ý người dùng gọi ngay hotline khẩn cấp (113, 115) hoặc hotline nhà bảo hiểm, yêu cầu giữ nguyên hiện trường.
  - Nếu **ĐƠN GIẢN** (is_complex = false): Chuyển tiếp sang Agent 2.

### Bước 3: Agent 2 - Coverage Pre-check (Kiểm tra bồi thường)
Chỉ chạy đối với các sự cố đơn giản (VD: tự quẹt trầy xước, vỡ gương khi đỗ xe).

- **RAG Context:** Dựa vào nhà bảo hiểm (VD: PTI), truy xuất các điều khoản "Phạm vi bảo hiểm" và "Các trường hợp loại trừ".
- **Phân tích LLM:** LLM đối chiếu mô tả sự cố với các điều khoản vừa truy xuất.
- **Quyết định:**
  - Nếu **ĐỦ ĐIỀU KIỆN** (is_eligible = true): Chuyển sang bước hướng dẫn sinh checklist hồ sơ (chụp ảnh góc nào, giấy tờ gì).
  - Nếu **KHÔNG ĐỦ ĐIỀU KIỆN** (is_eligible = false): Cảnh báo người dùng sự cố này có thể bị từ chối bồi thường (VD: mất cắp bộ phận nhưng hợp đồng chỉ đền bù mất cắp toàn bộ), gợi ý người dùng tự sửa chữa để tiết kiệm thời gian làm hồ sơ.

---

## 3. Công nghệ sử dụng (Tech Stack)

| Thành phần | Công nghệ | Lý do lựa chọn |
|---|---|---|
| **LLM Engine** | OpenAI API (gpt-4o-mini) | Tốc độ phản hồi nhanh, giá rẻ, khả năng parse JSON chính xác 100%. |
| **Vector Database** | ChromaDB (Local) | Chạy local không cần cloud DB, dễ dàng đóng gói vào Docker. |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) | Chạy CPU cực nhanh, miễn phí, không phụ thuộc OpenAI API Key cho phần embeddings. |
| **API Framework** | FastAPI (Python) | Xử lý async tốt, tự động sinh Swagger UI (OpenAPI docs). |

---

## 4. RAG Module (Retrieval-Augmented Generation)

Thay vì gửi toàn bộ cuốn luật bảo hiểm dài hàng trăm trang cho LLM (vừa tốn token, vừa dễ làm LLM bị "loãng" thông tin), hệ thống sử dụng RAG:

1. **Indexing (Chỉ chạy 1 lần):**
   - Đọc các file text (`policy_baoviet.txt`, `policy_pti.txt`).
   - Chia nhỏ thành các đoạn (chunks) khoảng 800 ký tự, có overlap 150 ký tự.
   - Biến đổi text thành vector embeddings (dùng ChromaDB default ONNX model).
   - Lưu vào thư mục `backend/app/agent/data/chroma_db`.

2. **Retrieval (Khi có request):**
   - Biến đổi mô tả sự cố thành vector.
   - Tìm kiếm 5 đoạn văn bản (chunks) có ý nghĩa tương đồng nhất trong DB (Cosine Similarity).
   - Ghép 5 đoạn này thành `Context` và nhét vào prompt gửi cho LLM.

---

## 5. Cấu trúc thư mục Agent

Toàn bộ code AI nằm trong `backend/app/agent/`:

```text
agent/
├── agents/
│   └── insurance_agents.py    # Logic cốt lõi của 2 Agent + gọi LLM
├── data/
│   ├── policy_baoviet.txt     # Dữ liệu luật Bảo Việt (text)
│   ├── policy_pti.txt         # Dữ liệu luật PTI (text)
│   └── dummy_incidents.json   # Dữ liệu test mẫu
├── models/
│   └── schemas.py             # Pydantic models (Input/Output validation)
├── rag/
│   ├── index_policies.py      # Script index dữ liệu vào ChromaDB
│   └── retriever.py           # Class truy xuất dữ liệu từ ChromaDB
└── routers/
    └── workflow.py            # FastAPI endpoints cho Agent
```

---

## 6. API Endpoints

Tất cả API có prefix `/api/v1/agent`. Bạn có thể test trực tiếp trên Swagger UI tại `http://localhost:3000/docs`.

### `POST /workflow/process-incident`
Endpoint chính để xử lý sự cố.

**Request Body (JSON):**
```json
{
  "time": "2024-06-16 14:00",
  "location": "Quận 1, TP.HCM",
  "description": "Xe bị trầy xước nhẹ ở cản sau khi đỗ xe",
  "incident_type": "tray_xuoc",
  "third_party_involved": false,
  "vehicle_drivable": true,
  "injuries": false,
  "insurer": "PTI"
}
```

**Response (JSON):**
```json
{
  "triage_result": {
    "is_complex": false,
    "description": "Sự cố trầy xước nhẹ, không có bên thứ ba, không thương tích."
  },
  "coverage_result": {
    "is_eligible": true,
    "description": "Thuộc phạm vi bảo hiểm vật chất xe cơ giới."
  },
  "next_step": "ELIGIBLE: Đủ điều kiện sơ bộ → Sinh checklist hồ sơ...",
  "assisted_mode": null
}
```

---

## 7. Cách mở rộng trong tương lai

1. **Thêm nhà bảo hiểm mới:** Chỉ cần copy file luật `.txt` vào thư mục `data/` và gọi lại API `POST /workflow/index-policies`.
2. **Hỗ trợ hình ảnh (Vision):** Nâng cấp Agent 1 để nhận ảnh hiện trường (dùng GPT-4o Vision) để tự động xác định mức độ hư hỏng thay vì chỉ dựa vào text mô tả.
3. **Agent 3 (Checklist Agent):** Sinh tự động danh sách các giấy tờ cần thiết dựa trên từng loại sự cố cụ thể.
