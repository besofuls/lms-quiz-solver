@echo off
chcp 65001 > nul
echo ================================================================
echo       ĐANG ĐÓNG GÓI ỨNG DỤNG THÀNH FILE LMS_Quiz_Solver_Pro.exe
echo ================================================================
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat

pyinstaller --noconsole --onefile ^
    --name "LMS_Quiz_Solver_Pro" ^
    --collect-all customtkinter ^
    --hidden-import=browser_use ^
    --hidden-import=google.genai ^
    --hidden-import=dotenv ^
    app.py

echo.
if exist "dist\LMS_Quiz_Solver_Pro.exe" (
    echo ================================================================
    echo  ✅ ĐÓNG GÓI THÀNH CÔNG!
    echo  File thực thi nằm tại: dist\LMS_Quiz_Solver_Pro.exe
    echo ================================================================
) else (
    echo ❌ Đóng gói thất bại. Hãy kiểm tra lại log bên trên.
)

pause
