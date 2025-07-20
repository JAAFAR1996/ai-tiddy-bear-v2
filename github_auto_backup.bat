@echo off
chcp 65001 >nul

REM إعداد المستخدم
set "PROJECT_DIR=C:\Users\jaafa\Desktop\5555\ai-teddy\ai-tiddy-bear--main"
set "GIT_BRANCH=main"

REM انتقل إلى مجلد المشروع
cd /d "%PROJECT_DIR%"
if errorlevel 1 (
    echo [خطأ] لا يمكن الوصول إلى %PROJECT_DIR%
    pause
    exit /b 1
)

REM تحقق من وجود git
if not exist ".git" (
    echo [خطأ] هذا المجلد ليس مستودع git!
    pause
    exit /b 1
)

REM احصل على التاريخ والوقت
for /f "tokens=2 delims==" %%I in ('"wmic os get localdatetime /value"') do set datetime=%%I
set TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%-%datetime:~10,2%

echo ====== بدأ النسخ الاحتياطي [%TIMESTAMP%] ======
echo Working directory: %CD%

REM أضف جميع الملفات
git add --all .

REM تحقق من وجود تغييرات
git diff --cached --quiet
if errorlevel 1 (
    git commit -m "Auto-backup %TIMESTAMP%"
    if errorlevel 1 (
        echo [خطأ] فشل الـ commit. (قد لا توجد تغييرات أو هناك خطأ)
        pause
        exit /b 1
    )
    git push origin %GIT_BRANCH%
    if errorlevel 1 (
        echo [خطأ] فشل push! تحقق من إعدادات الريموت أو الفرع أو الانترنت أو المصادقة.
        pause
        exit /b 1
    )
    echo [تم] كل التغييرات رفعت بنجاح [%TIMESTAMP%]
    git log -1 --oneline
) else (
    echo لا توجد تغييرات جديدة لرفعها [%TIMESTAMP%]
)

git status
pause
