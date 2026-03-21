# ============================================================
# Dockerfile - LotusHacks AI Agent Backend
# Base: Python 3.11-slim
# ============================================================

FROM python:3.11-slim

# --- Metadata ---
LABEL maintainer="LotusHacks Team"
LABEL description="AI Agent Backend for LotusHacks Insurance Claim Automation"

# --- System dependencies ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --- Working directory ---
WORKDIR /app

# --- Install Python dependencies ---
# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy application source code ---
COPY . .

# --- Create data directory for ChromaDB persistence ---
RUN mkdir -p /app/app/data/chroma_db

# --- Expose port ---
EXPOSE 8000

# --- Health check ---
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# --- Start server ---
# Sử dụng uvicorn với reload=False cho production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
