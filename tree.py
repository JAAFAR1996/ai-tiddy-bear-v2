import os
from termcolor import colored
import sys

ALLOWED_ROOT = {
    # ... كما سبق ...
    '.gitignore',  # لاحظ: فقط .gitignore، أما مجلد .git يجب منعه
    # ...
}
GLOBAL_DENYLIST = {
    '__pycache__', '.venv', 'venv', 'env', '.idea', '.vscode', 'dist', 'build', 'node_modules', '.git'
}
JUNK_SUFFIX = {'.pyc', '.pyo', '.swp', '.swo', '.log', '.bak'}

found_issues = []

def is_junk(name):
    return (
        name in GLOBAL_DENYLIST
        or any(name.endswith(suffix) for suffix in JUNK_SUFFIX)
        or name.startswith('.DS_Store')
    )

def print_tree(path, allowed=None, prefix=''):
    items = [f for f in os.listdir(path) if not is_junk(f)]
    items = sorted(items)
    for idx, item in enumerate(items):
        p = os.path.join(path, item)
        # تجاهل مجلد .git مباشرة (لن تدخل حتى بداخله)
        if item == '.git':
            continue

        connector = '└── ' if idx == len(items) - 1 else '├── '
        color = None

        if is_junk(item):
            color = 'yellow'
            found_issues.append(f'JUNK: {p}')
        elif allowed is not None and item not in allowed:
            color = 'red'
            found_issues.append(f'UNALLOWED: {p}')

        if color:
            print(prefix + connector + colored(item, color, attrs=['bold']))
        else:
            print(prefix + connector + item)

        # لا تنزل داخل أي مجلد ممنوع (ومنها .git)
        if os.path.isdir(p) and item not in GLOBAL_DENYLIST:
            sub_allowed = None
            print_tree(p, sub_allowed, prefix + ('    ' if idx == len(items)-1 else '│   '))

if __name__ == '__main__':
    print_tree('.', ALLOWED_ROOT)
    if found_issues:
        print(colored(f'\n[!] WARNING: Found {len(found_issues)} issues (unallowed or junk files/directories):', 'red', attrs=['bold']))
        for issue in found_issues:
            print(colored(issue, 'red' if issue.startswith('UNALLOWED') else 'yellow'))
        sys.exit(1)
    else:
        print(colored('\nProject tree is CLEAN. No unallowed or junk files found.', 'green', attrs=['bold']))
