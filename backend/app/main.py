"""
LotusHacks Backend - Main FastAPI Application

Modules:
    - auth:  Xác thực người dùng (signup, signin, Google OAuth)
    - agent: AI Agent workflow (Triage + Coverage + RAG)

Chạy local:
    cd backend
    uvicorn app.main:app --reload --port 8000
    # Server: http://localhost:8000
    # Swagger: http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import close_db, init_db
from app.auth.routers.auth import router as auth_router
from app.agent.routers.workflow import router as agent_workflow_router
from app.core.config import agent_settings

app = FastAPI(
    title="LotusHacks API",
    description=(
        "Backend API cho LotusHacks - Hệ thống tự động hóa bồi thường bảo hiểm ô tô.\n\n"
        "**Modules:**\n"
        "- `/auth` - Xác thực người dùng (signup, signin, Google OAuth)\n"
        "- `/api/v1/agent` - AI Agent workflow (Triage + Coverage + RAG)\n"
    ),
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=agent_settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(auth_router)
app.include_router(agent_workflow_router, prefix="/api/v1/agent")


# --- Lifecycle Events ---
@app.on_event("startup")
async def on_startup():
    """Khởi tạo database connection khi server start."""
    init_db()


@app.on_event("shutdown")
async def on_shutdown():
    """Đóng database connection khi server shutdown."""
    close_db()


# --- Health Check ---
@app.get("/health", tags=["Health"])
async def health_check():
    """Kiểm tra trạng thái server."""
    return {"status": "ok", "version": "0.2.0"}
