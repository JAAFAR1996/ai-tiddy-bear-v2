def split_report_precise(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    parts = {}
    current_part = None
    allowed_parts = ['مشاكل الأمان', 'مشاكل جودة الكود', 'مشاكل بيئة الفحص']

    for line in lines:
        if line.startswith('## '):
            title = line.strip().strip('# ').strip()
            if title in allowed_parts:
                current_part = title
                parts[current_part] = []
            else:
                current_part = None
        if current_part:
            parts[current_part].append(line)

    for part_name, content in parts.items():
        filename = part_name.replace(' ', '_') + '.md'
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(content)
        print(f'Created file: {filename}')


if __name__ == '__main__':
    split_report_precise('audit_report_ai_teddy_20250719_124802.md')
