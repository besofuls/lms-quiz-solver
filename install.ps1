# Script tải và khởi chạy nhanh LMS Quiz Solver Pro dành cho Windows
$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   🎓 LMS QUIZ SOLVER PRO - TẢI VÀ CHẠY NHANH TỰ ĐỘNG     " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

$downloadUrl = "https://github.com/besofuls/lms-quiz-solver/releases/latest/download/LMS_Quiz_Solver_Pro.exe"
$destFolder = "$HOME\Downloads\LMS_Quiz_Solver"
$destExe = "$destFolder\LMS_Quiz_Solver_Pro.exe"

if (!(Test-Path $destFolder)) {
    New-Item -ItemType Directory -Path $destFolder | Out-Null
}

Write-Host "`n⏳ Đang tải ứng dụng LMS_Quiz_Solver_Pro.exe..." -ForegroundColor Green
try {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $destExe -UseBasicParsing
    Write-Host "✅ Tải thành công! Đang khởi động phần mềm..." -ForegroundColor Green
    Start-Process -FilePath $destExe
} catch {
    Write-Host "⚠️ Chưa tìm thấy bản Release trên GitHub hoặc mạng bị gián đoạn." -ForegroundColor Red
    Write-Host "👉 Bạn có thể tải mã nguồn về và nhấp đúp file 'QuickStart.bat' để chạy!" -ForegroundColor Yellow
}
