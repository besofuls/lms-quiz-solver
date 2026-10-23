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
    --exclude-module anthropic ^
    --exclude-module groq ^
    --exclude-module ollama ^
    --exclude-module openai ^
    --exclude-module pypdf ^
    --exclude-module reportlab ^
    --exclude-module docx ^
    --exclude-module mcp ^
    app.py

if exist "dist\LMS_Quiz_Solver_Pro.exe" (
    copy /y "dist\LMS_Quiz_Solver_Pro.exe" "LMS_Quiz_Solver_Pro.exe" > nul
    echo.
    echo ================================================================
    echo  [OK] ĐÓNG GÓI THÀNH CÔNG!
    echo  File thực thi: LMS_Quiz_Solver_Pro.exe
    echo ================================================================
) else (
    echo [ERROR] Đóng gói thất bại. Hãy kiểm tra lại log bên trên.
)

pause
