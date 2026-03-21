"""
LotusHacks AI Agent Backend - Main FastAPI Application
Tích hợp: Auth module + AI Agent workflow (Triage + Coverage)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import close_db, init_db
from app.routers.auth import router as auth_router
from app.routers.agent.workflow import router as agent_workflow_router
from app.core.config import agent_settings

app = FastAPI(
    title="LotusHacks AI Agent API",
    description=(
        "Backend API cho hệ thống tự động hóa bồi thường bảo hiểm ô tô. "
        "Bao gồm 2 AI Agent: Triage Agent (phân loại sự cố) và Coverage Agent (kiểm tra điều kiện bồi thường)."
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
