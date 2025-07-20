import re

def sanitize_filename(name):
    # استبدال أي رمز غير مسموح به في اسم الملف بـ "_"
    return re.sub(r'[\\/:"*?<>|]+', '_', name)

def split_problems_by_section(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    sections = {}
    current_section = None

    for line in lines:
        if line.startswith('## '):
            section_title = line.strip().replace('## ', '').replace(' ', '_')
            section_title = sanitize_filename(section_title)
            current_section = section_title
            sections[current_section] = []
        if current_section:
            sections[current_section].append(line)

    for section, content in sections.items():
        filename = f"{section}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(content)
        print(f"✅ كتب القسم: {filename}")

if __name__ == '__main__':
    split_problems_by_section('audit_report_ai_teddy_20250720_113809.md')
