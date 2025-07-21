import os
import ast

PROJECT_DIR = "src"  # غيّر المسار إذا لزم الأمر

def find_py_files(root):
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith(".py"):
                yield os.path.join(dirpath, filename)

def get_defs_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)
    defs = set()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            defs.add(node.name)
    return defs

def import_targets(node):
    if isinstance(node, ast.ImportFrom):
        mod = node.module
        for n in node.names:
            yield (mod, n.name, node.lineno)
    elif isinstance(node, ast.Import):
        for n in node.names:
            yield (n.name, n.asname or n.name, node.lineno)

def check_imports():
    errors = []
    py_files = list(find_py_files(PROJECT_DIR))
    module_defs = {}

    # Pre-scan all files for defined class/function names
    for file_path in py_files:
        rel_path = os.path.relpath(file_path, PROJECT_DIR)
        mod = rel_path.replace(os.sep, ".")[:-3]  # remove .py
        module_defs[mod] = get_defs_from_file(file_path)

    # Now check all imports
    for file_path in py_files:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=file_path)
        for node in ast.iter_child_nodes(tree):
            for mod, name, lineno in import_targets(node):
                if not mod or "." not in mod:
                    continue
                mod_path = mod
                # relative imports
                if mod_path.startswith(".."):
                    continue
                # Try to resolve imported module file
                if mod_path.startswith(PROJECT_DIR.replace("/", ".")):
                    mod_path = mod_path[len(PROJECT_DIR.replace("/", ".")) + 1 :]
                # Check in module_defs
                if mod_path in module_defs:
                    defs = module_defs[mod_path]
                    if name not in defs:
                        errors.append(
                            f"{file_path}:{lineno}: '{name}' NOT FOUND in module '{mod_path}'"
                        )

    if errors:
        print("\n".join(errors))
        print(f"\n{len(errors)} broken imports detected!")
    else:
        print("✅ All imports found and valid.")

if __name__ == "__main__":
    check_imports()