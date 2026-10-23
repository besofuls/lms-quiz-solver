@echo off
chcp 65001 > nul
title Tu Dong Giai Quiz AI - 3 Gemini Keys + Edge
cls

echo ================================================================
echo   CHƯƠNG TRÌNH GIẢI QUIZ AI SIÊU TỐC (3 GEMINI KEYS XOAY TUA)
echo ================================================================
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat

python lms_quiz_solver.py

pause
