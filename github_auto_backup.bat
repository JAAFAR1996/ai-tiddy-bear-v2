@echo off
chcp 65001 >nul

REM Configure git credentials once if not set
git config --global credential.helper store

REM Get current datetime in yyyy-mm-dd_hh-mm format
for /f "tokens=2 delims==" %%I in ('"wmic os get localdatetime /value"') do set datetime=%%I
set TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%-%datetime:~10,2%

REM Change directory to your project
cd /d "C:\Users\jaafa\Desktop\5555\ai-teddy\ai-tiddy-bear--main"

echo Running auto-backup for: %CD%

REM Add all files (new/modified/deleted)
git add --all .

REM Check for staged changes
git diff --cached --quiet
if %ERRORLEVEL% EQU 0 (
    echo No new changes to commit. %TIMESTAMP%
) else (
    git commit -m "Auto-backup %TIMESTAMP%"
    git push origin main
    echo All changes pushed. %TIMESTAMP%
    git log -1 --oneline
)

git status
pause
