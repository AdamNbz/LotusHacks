#!/bin/bash
# ============================================================
# LotusHacks - Run All Tests (Linux/Mac)
# Usage: bash run-tests.sh
# ============================================================

set -e

echo ""
echo "============================================================"
echo "  LotusHacks - Test Runner (Linux/Mac)"
echo "============================================================"
echo ""

BACKEND_RESULT=0
FRONTEND_RESULT=0

# ============================================================
# [1/3] Backend Tests
# ============================================================
echo "============================================================"
echo "  [1/3] Backend Unit Tests (Agent + Auth)"
echo "============================================================"
echo ""

cd backend

# Tạo venv nếu chưa có
if [ ! -d "venv" ]; then
    echo "[INFO] Tạo virtual environment..."
    python3 -m venv venv
fi

# Kích hoạt venv
echo "[INFO] Kích hoạt venv..."
source venv/bin/activate

# Cài dependencies
echo "[INFO] Cài đặt dependencies..."
pip install -r requirements.txt -q

# Set env vars cho test
export OPENAI_API_KEY="test-key-for-unit-tests"
export MONGODB_URI="mongodb://localhost:27017"
export JWT_SECRET="test-secret"

# Chạy pytest
echo ""
echo "--- Running pytest ---"
python -m pytest tests/ -v --tb=short || BACKEND_RESULT=1

deactivate
cd ..

echo ""

# ============================================================
# [2/3] Frontend Tests
# ============================================================
echo "============================================================"
echo "  [2/3] Frontend Unit Tests (React + Vitest)"
echo "============================================================"
echo ""

cd frontend

# Cài npm dependencies nếu chưa có
if [ ! -d "node_modules" ]; then
    echo "[INFO] Cài đặt npm dependencies..."
    npm install
fi

# Chạy vitest
echo ""
echo "--- Running vitest ---"
npx vitest run || FRONTEND_RESULT=1

cd ..

echo ""

# ============================================================
# [3/3] Summary
# ============================================================
echo "============================================================"
echo "  [3/3] Test Summary"
echo "============================================================"
echo ""

if [ $BACKEND_RESULT -eq 0 ]; then
    echo "  Backend Tests:  PASSED ✓"
else
    echo "  Backend Tests:  FAILED ✗"
fi

if [ $FRONTEND_RESULT -eq 0 ]; then
    echo "  Frontend Tests: PASSED ✓"
else
    echo "  Frontend Tests: FAILED ✗"
fi

echo ""
echo "============================================================"
echo ""

# Exit code
if [ $BACKEND_RESULT -ne 0 ] || [ $FRONTEND_RESULT -ne 0 ]; then
    exit 1
fi
