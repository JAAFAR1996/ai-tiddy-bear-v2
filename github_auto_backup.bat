@echo off
chcp 65001 >nul

:: إعداد Git credentials مرة واحدة (إن لم تُفعلها من قبل)
git config --global credential.helper store

:: إعداد التاريخ والوقت لتضمينه في رسالة الكوميت
for /f "tokens=1-4 delims=/ " %%a in ("%DATE%") do (
    set DD=%%a & set MM=%%b & set YYYY=%%c
)
set CURRENT_TIME=%TIME: =0%
set TIMESTAMP=%YYYY%-%MM%-%DD%_%CURRENT_TIME:~0,2%-%CURRENT_TIME:~3,2%

cd /d "C:\Users\jaafa\Desktop\5555\ai-teddy\backend"
echo 🔁 Running auto-backup for: %CD%

git add -A

git diff --quiet --exit-code
if %ERRORLEVEL% EQU 0 (
    echo ✅ لا توجد تغييرات لرفعها. %TIMESTAMP%
) else (
    git commit -m "Auto-backup %TIMESTAMP%"
    git push origin main
    git fetch origin main
    echo ✅ التغييرات تم رفعها.
    git log -1 --oneline
)

git status
pause
