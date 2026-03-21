# ============================================================
# LotusHacks - Run All Tests (Windows PowerShell)
# Usage: .\run-tests.ps1
# ============================================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  LotusHacks - Test Runner (PowerShell)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# --- Kiểm tra prerequisites ---
$pythonOk = Get-Command python -ErrorAction SilentlyContinue
$nodeOk = Get-Command node -ErrorAction SilentlyContinue

if (-not $pythonOk) {
    Write-Host "[ERROR] Python chưa được cài đặt." -ForegroundColor Red
    Write-Host "Tải tại: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
if (-not $nodeOk) {
    Write-Host "[ERROR] Node.js chưa được cài đặt." -ForegroundColor Red
    Write-Host "Tải tại: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host "Python: $(python --version)" -ForegroundColor Green
Write-Host "Node:   $(node --version)" -ForegroundColor Green
Write-Host ""

# ============================================================
# [1/3] Backend Tests
# ============================================================
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  [1/3] Backend Unit Tests (Agent + Auth)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Push-Location backend

# Tạo venv nếu chưa có
if (-not (Test-Path "venv")) {
    Write-Host "[INFO] Tạo virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Kích hoạt venv
Write-Host "[INFO] Kích hoạt venv..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Cài dependencies
Write-Host "[INFO] Cài đặt dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt -q

# Set env vars cho test
$env:OPENAI_API_KEY = "test-key-for-unit-tests"
$env:MONGODB_URI = "mongodb://localhost:27017"
$env:JWT_SECRET = "test-secret"

# Chạy pytest
Write-Host ""
Write-Host "--- Running pytest ---" -ForegroundColor Yellow
python -m pytest tests/ -v --tb=short
$backendResult = $LASTEXITCODE

deactivate
Pop-Location

Write-Host ""

# ============================================================
# [2/3] Frontend Tests
# ============================================================
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  [2/3] Frontend Unit Tests (React + Vitest)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Push-Location frontend

# Cài npm dependencies nếu chưa có
if (-not (Test-Path "node_modules")) {
    Write-Host "[INFO] Cài đặt npm dependencies..." -ForegroundColor Yellow
    npm install
}

# Chạy vitest
Write-Host ""
Write-Host "--- Running vitest ---" -ForegroundColor Yellow
npx vitest run
$frontendResult = $LASTEXITCODE

Pop-Location

Write-Host ""

# ============================================================
# [3/3] Summary
# ============================================================
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  [3/3] Test Summary" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

if ($backendResult -eq 0) {
    Write-Host "  Backend Tests:  PASSED" -ForegroundColor Green
} else {
    Write-Host "  Backend Tests:  FAILED" -ForegroundColor Red
}

if ($frontendResult -eq 0) {
    Write-Host "  Frontend Tests: PASSED" -ForegroundColor Green
} else {
    Write-Host "  Frontend Tests: FAILED" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Exit code
if (($backendResult -ne 0) -or ($frontendResult -ne 0)) {
    exit 1
}
