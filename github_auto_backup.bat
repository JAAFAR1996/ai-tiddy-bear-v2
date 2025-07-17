@echo off
chcp 65001 >nul

REM إعداد Git credentials مرة واحدة (إذا لم تفعلها سابقًا)
git config --global credential.helper store

REM التقاط التاريخ والوقت بشكل موثوق (yyyy-mm-dd_hh-mm)
for /f "tokens=2 delims==" %%I in ('"wmic os get localdatetime /value"') do set datetime=%%I
set TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%-%datetime:~10,2%

REM انتقل لمجلد المشروع الجديد
cd /d "C:\Users\jaafa\Desktop\5555\ai-teddy\ai-tiddy-bear--main"

echo 🔁 Running auto-backup for: %CD%

REM تحديث المشروع من الريموت (لحل أي تعارض قبل الدفع)
git pull origin main

REM إضافة كل التغييرات
git add -A

REM التحقق هل هناك تغييرات
git diff --cached --quiet
if %ERRORLEVEL% EQU 0 (
    echo ✅ لا توجد تغييرات لرفعها. %TIMESTAMP%
) else (
    git commit -m "Auto-backup %TIMESTAMP%"
    git push origin main
    echo ✅ التغييرات تم رفعها.
    git log -1 --oneline
)

git status
pause
