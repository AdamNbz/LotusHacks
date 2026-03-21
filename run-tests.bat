@echo off
REM ============================================================
REM LotusHacks - Run All Tests (Windows)
REM Usage: double-click hoặc chạy trong CMD/PowerShell
REM ============================================================

echo.
echo ============================================================
echo   LotusHacks - Test Runner (Windows)
echo ============================================================
echo.

REM --- Kiểm tra Python ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python chưa được cài đặt. Tải tại: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM --- Kiểm tra Node.js ---
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js chưa được cài đặt. Tải tại: https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   [1/3] Backend Unit Tests (Agent + Auth)
echo ============================================================
echo.

cd backend
if not exist "venv" (
    echo [INFO] Tạo virtual environment...
    python -m venv venv
)

echo [INFO] Kích hoạt venv...
call venv\Scripts\activate.bat

echo [INFO] Cài đặt dependencies...
pip install -r requirements.txt -q

echo.
echo --- Running pytest ---
set OPENAI_API_KEY=test-key-for-unit-tests
set MONGODB_URI=mongodb://localhost:27017
set JWT_SECRET=test-secret
python -m pytest tests/ -v --tb=short
set BACKEND_RESULT=%errorlevel%

call deactivate
cd ..

echo.
echo ============================================================
echo   [2/3] Frontend Unit Tests (React + Vitest)
echo ============================================================
echo.

cd frontend
if not exist "node_modules" (
    echo [INFO] Cài đặt npm dependencies...
    npm install
)

echo.
echo --- Running vitest ---
npx vitest run
set FRONTEND_RESULT=%errorlevel%

cd ..

echo.
echo ============================================================
echo   [3/3] Test Summary
echo ============================================================
echo.

if %BACKEND_RESULT% equ 0 (
    echo   Backend Tests:  PASSED ✓
) else (
    echo   Backend Tests:  FAILED ✗
)

if %FRONTEND_RESULT% equ 0 (
    echo   Frontend Tests: PASSED ✓
) else (
    echo   Frontend Tests: FAILED ✗
)

echo.
echo ============================================================
echo.
pause
