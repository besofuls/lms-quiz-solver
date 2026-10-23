@echo off
chcp 65001 > nul
title LMS Quiz Solver Pro - Tự Động Khởi Động
cd /d "%~dp0"

echo ================================================================
echo       LMS QUIZ SOLVER PRO - TỰ ĐỘNG THIẾT LẬP VÀ MỞ ỨNG DỤNG
echo ================================================================
echo.

:: 1. Kiểm tra Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [LỖI] Máy tính của bạn chưa cài đặt Python!
    echo Vui lòng tải Python từ trang chủ: https://www.python.org
    pause
    exit /b
)

:: 2. Tự động tạo venv và cài thư viện nếu chưa có (chỉ làm 1 lần duy nhất)
if not exist ".venv" (
    echo [1/2] Đang tự động thiết lập môi trường (chỉ mất 1-2 phút lần đầu)...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo [2/2] Đang tải các thư viện cần thiết...
    pip install -r requirements.txt
    playwright install chromium
) else (
    call .venv\Scripts\activate.bat
)

:: 3. Khởi chạy giao diện app
echo.
echo [OK] Đang khởi động giao diện phần mềm...
start "" python app.py
