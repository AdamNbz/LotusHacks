# LotusHacks - Automated Auto Insurance Claim System

Chào mừng bạn đến với dự án website Hackathon của chúng tôi! Hệ thống tự động hóa quy trình bồi thường bảo hiểm ô tô sử dụng AI Agents và RAG (Retrieval-Augmented Generation).

Hệ thống giúp phân loại sự cố, kiểm tra điều kiện bồi thường sơ bộ, và hướng dẫn người dùng theo thời gian thực dựa trên hợp đồng bảo hiểm thực tế.

## 🌟 Tính năng AI chính

- **AI Triage Agent:** Phân loại sự cố tự động (Phức tạp/Đơn giản) dựa trên mức độ nghiêm trọng.
- **AI Coverage Agent:** Đánh giá sơ bộ khả năng bồi thường dựa trên điều khoản bảo hiểm (RAG).
- **RAG Vectorstore:** Lưu trữ và truy xuất các điều khoản bảo hiểm từ ChromaDB.

## 📁 Cấu trúc thư mục (Directory Structure)

```text
LotusHacks/
├── backend/                  # FastAPI Backend (Auth + AI Agent)
│   ├── app/
│   │   ├── agent/            # AI Agent Module (Triage, Coverage, RAG)
│   │   ├── auth/             # Authentication Module (JWT, Google OAuth)
│   │   └── core/             # Cấu hình chung
│   ├── tests/                # Unit tests cho Backend (Agent + Auth)
│   └── Dockerfile            # Dockerfile cho Backend
├── frontend/                 # React + Vite Frontend
│   ├── src/
│   │   ├── components/       # UI Components
│   │   ├── pages/            # React Router Pages
│   │   └── test/             # Unit tests cho Frontend
│   └── Dockerfile            # Dockerfile cho Frontend (Nginx)
├── docker-compose.yml        # Docker compose chạy toàn bộ stack
├── run-tests.bat             # Script chạy tests trên Windows
└── run-tests.sh              # Script chạy tests trên Linux/Mac
```

## 🛠️ Công nghệ đề xuất (Tech Stack)

- **Frontend:** [Vite](https://vitejs.dev/) + [React](https://react.dev/) + TypeScript, Tailwind CSS, shadcn/ui.
- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python), Uvicorn.
- **Database:** [MongoDB](https://www.mongodb.com/) (NoSQL).
- **AI/ML:** OpenAI API, ChromaDB (Local Vectorstore), Sentence-Transformers.
- **Testing:** Pytest (Backend), Vitest (Frontend).
- **Deployment:** Docker & Docker Compose.

---

## 🚀 Hướng dẫn chạy nhanh (Docker)

Cách dễ nhất để chạy toàn bộ hệ thống là sử dụng Docker.

### 1. Cấu hình môi trường:
```bash
cp .env.example .env
```
*Mở file `.env` và điền `OPENAI_API_KEY=sk-...`*

### 2. Khởi động hệ thống:
```bash
docker-compose up --build
```

### 3. Truy cập:
- **Frontend:** http://localhost:3000
- **Backend API Docs:** http://localhost:3000/docs
- **FastAPI Direct:** http://localhost:8000

---

## 💻 Hướng dẫn chạy Local (Không dùng Docker)

### 1. Chạy Backend
```bash
cd backend
cp .env.example .env      # Sửa OPENAI_API_KEY trong file .env

python -m venv venv
# Kích hoạt venv (Windows): venv\Scripts\activate
# Kích hoạt venv (Mac/Linux): source venv/bin/activate

pip install -r requirements.txt

# Index dữ liệu RAG (Chỉ chạy lần đầu)
python -m app.agent.rag.index_policies

# Khởi động server
python -m app.main
```
Backend sẽ chạy tại: http://localhost:8000

### 2. Chạy Frontend
Mở terminal mới:
```bash
cd frontend
npm install
npm run dev
```
Frontend sẽ chạy tại: http://localhost:8080

---

## 🧪 Hướng dẫn chạy Unit Tests

Dự án đi kèm với hệ thống Unit Tests toàn diện cho cả Backend (pytest) và Frontend (vitest).

### Chạy trên Windows:
Mở PowerShell hoặc CMD tại thư mục gốc và chạy:
```cmd
.\run-tests.bat
# Hoặc: .\run-tests.ps1
```

### Chạy trên Linux/Mac:
Mở terminal tại thư mục gốc và chạy:
```bash
bash run-tests.sh
```

---

## 🧹 Hướng dẫn xóa sạch (Clean up)

Nếu bạn muốn xóa toàn bộ hệ thống để làm lại từ đầu (bao gồm xóa database, ChromaDB, venv, node_modules):

### Nếu dùng Docker:
```bash
docker-compose down -v --rmi all
```

### Nếu chạy Local:
**Trên Windows:**
```cmd
# Xóa backend venv & ChromaDB
cd backend
rmdir /s /q venv
rmdir /s /q app\agent\data\chroma_db

# Xóa frontend node_modules
cd ..\frontend
rmdir /s /q node_modules
```

**Trên Mac/Linux:**
```bash
# Xóa backend venv & ChromaDB
cd backend
rm -rf venv
rm -rf app/agent/data/chroma_db

# Xóa frontend node_modules
cd ../frontend
rm -rf node_modules
```

---

## 📚 Tài liệu chi tiết

Để hiểu rõ hơn về kiến trúc AI và cách hoạt động của các Agents, vui lòng xem file [AI_SERVICES.md](AI_SERVICES.md).

## 👥 Thành viên nhóm (Team Members)

- Đinh Việt Phát - Project Manager
- Nguyễn Võ Ngọc Bảo - Fullstack Developer
- Phan Quốc Đại Sơn - AI/ML Developer
- Bùi Nhật Anh Khôi - AI/ML Developer
