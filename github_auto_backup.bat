@echo off
REM ====== GitHub Auto Backup Script (Enhanced) ======
REM يتجاوز pre-commit hooks للرفع الطارئ
REM تأكد أنك نفذت git config --global user.name و user.email مسبقاً

setlocal enabledelayedexpansion

echo ========================================
echo   GitHub Auto Backup (Force Mode)
echo ========================================
echo.

REM اسم البرانش الحالي
for /f "delims=" %%b in ('git branch --show-current') do set "branch=%%b"
echo Current branch: %branch%

REM تاريخ ووقت النسخة
for /f "delims=" %%t in ('wmic os get localdatetime ^| find "."') do set datetime=%%t
set datetime=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%-%datetime:~10,2%

REM إضافة جميع الملفات (بما في ذلك المحذوفة والمنقولة)
echo.
echo Adding all files...
git add -A

REM عرض الملفات المضافة
echo.
echo Files to be committed:
git status --short

REM عمل commit مع تجاوز pre-commit hooks
echo.
echo Creating commit (bypassing hooks)...
git commit --no-verify -m "[%datetime%] Auto backup"

if %ERRORLEVEL% EQU 0 (
    echo Commit successful!
    
    REM رفع الملفات
    echo.
    echo Pushing to origin/%branch%...
    git push origin %branch%
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ✓ Push successful!
    ) else (
        echo.
        echo ✗ Push failed! Trying with force-with-lease...
        git push origin %branch% --force-with-lease
    )
) else (
    echo.
    echo ✗ Commit failed! (Maybe no changes to commit?)
)

REM الحالة النهائية
echo.
echo ========================================
echo Final status:
echo ========================================
git status

echo.
echo ========================================
echo WARNING: Pre-commit hooks were bypassed!
echo Remember to fix any code issues later.
echo ========================================
echo.

pause