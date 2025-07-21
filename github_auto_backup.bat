@echo off
REM ====== GitHub Auto Backup Script ======
REM تأكد أنك نفذت git config --global user.name و user.email مسبقاً
REM يجب أن يكون git منصّب ومتاح في PATH

setlocal enabledelayedexpansion

REM اسم البرانش الحالي
for /f "delims=" %%b in ('git branch --show-current') do set "branch=%%b"

REM تاريخ ووقت النسخة
for /f "delims=" %%t in ('wmic os get localdatetime ^| find "."') do set datetime=%%t
set datetime=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%-%datetime:~10,2%

REM إضافة جميع الملفات
git add .

REM عمل commit باسم وتاريخ محدد
git commit -m "[%datetime%] Auto backup"

REM رفع الملفات
git push origin %branch%

REM الحالة النهائية
git status

pause
