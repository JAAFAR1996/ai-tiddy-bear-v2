@echo off
chcp 65001 >nul

REM إعداد متغيرات المشروع
set "PROJECT_DIR=C:\Users\jaafa\Desktop\5555\ai-teddy\ai-tiddy-bear--main"
set "GIT_BRANCH=main"
set "GIT_REMOTE=https://github.com/JAAFAR1996/ai-tiddy-bear-v2.git"

cd /d "%PROJECT_DIR%"
if errorlevel 1 (
    echo [ERROR] Cannot access %PROJECT_DIR%
    pause
    exit /b 1
)

REM Ensure this is a git repo
if not exist ".git" (
    echo [ERROR] Not a git repository!
    pause
    exit /b 1
)

git remote set-url origin %GIT_REMOTE%

REM Get datetime for commit message
for /f "tokens=2 delims==" %%I in ('"wmic os get localdatetime /value"') do set datetime=%%I
set TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%-%datetime:~10,2%

git add .

REM Check if there are staged changes
git diff --cached --quiet
if errorlevel 1 (
    git commit -m "Auto-backup %TIMESTAMP%"
    if errorlevel 1 (
        echo [ERROR] Commit failed.
        pause
        exit /b 1
    )
    git push origin %GIT_BRANCH%
    if errorlevel 1 (
        echo [ERROR] Push failed!
        pause
        exit /b 1
    )
    echo [SUCCESS] All changes pushed. [%TIMESTAMP%]
    git log -1 --oneline
) else (
    echo No new changes to commit. [%TIMESTAMP%]
)

git status
pause
