import os
import py_compile

project = r"C:\Users\jaafa\Desktop\5555\ai-teddy\ai-tiddy-bear--main\src"
errors = []

# تفحص كل ملفات .py
for root, _, files in os.walk(project):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            try:
                py_compile.compile(path, doraise=True)
            except py_compile.PyCompileError as e:
                errors.append(str(e))

# اكتب الأخطاء إلى ملف
with open("errors.txt", "w", encoding="utf-8") as out:
    out.write("\n".join(errors))

# إخراج توضيحي
if errors:
    print(f"تم العثور على {len(errors)} ملف/ملفات بها SyntaxError، انظر errors.txt")
else:
    print("لا توجد Syntax Errors.")
