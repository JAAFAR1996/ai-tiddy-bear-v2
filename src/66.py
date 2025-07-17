import re

with open("errors.txt", encoding="utf8") as f:
    lines = f.readlines()

results = []

# النمط الذي يمسك المسار والسطر
pattern = re.compile(r'File "(.*?)", line (\d+)')

for line in lines:
    m = pattern.search(line)
    if m:
        path = m.group(1)
        lineno = m.group(2)
        # ترتيب الناتج بنفس الصيغة المطلوبة
        # إذا تريد المسار يبدأ بعد src فقط:
        idx = path.find('src')
        if idx != -1:
            path = path[idx:]
        results.append(f"{path}:{lineno}")

# حذف التكرار + ترتيب النتائج
unique_sorted = sorted(set(results))

for entry in unique_sorted:
    print(entry)
