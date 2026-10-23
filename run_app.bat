@echo off
chcp 65001 > nul
title LMS Quiz Solver Pro - AI Trợ Lý Tự Động
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python app.py
