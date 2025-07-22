#!/usr/bin/env python3
import ast
import os

TARGET_USER_CLASS = "User"
USER_IMPORT_PATH = "from src.domain.entities.user import User"
REPORT_FILE = "reports/user_dict_violations.log"

def analyze_file(path):
    findings = []
    try:
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=path)
    except Exception:
        return findings

    imports_user = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and "user" in node.module.lower():
                for n in node.names:
                    if n.name == TARGET_USER_CLASS:
                        imports_user = True
        if isinstance(node, ast.Assign):
            if (isinstance(node.targets[0], ast.Name) and
                node.targets[0].id in ("user", "current_user") and
                isinstance(node.value, ast.Dict)):
                findings.append((node.lineno, "Assign user as dict"))
        if isinstance(node, ast.Return):
            if isinstance(node.value, ast.Dict):
                findings.append((node.lineno, "Return dict"))
            elif (isinstance(node.value, ast.Call) and
                  isinstance(node.value.func, ast.Name) and
                  node.value.func.id == "dict"):
                findings.append((node.lineno, "Return dict()"))
        if isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                if arg.arg in ("user", "current_user"):
                    if not (arg.annotation and hasattr(arg.annotation, "id") and arg.annotation.id == TARGET_USER_CLASS):
                        findings.append((node.lineno, "Endpoint arg 'user' missing User type"))
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
            if "user" in content and USER_IMPORT_PATH not in content:
                findings.append((0, "File uses 'user' but does not import User class"))
    except Exception:
        pass
    return findings

def scan_project(root_dir="src"):
    results = {}
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if not fname.endswith(".py"):
                continue
            path = os.path.join(dirpath, fname)
            findings = analyze_file(path)
            if findings:
                results[path] = findings
    return results

if __name__ == "__main__":
    results = scan_project("src")
    os.makedirs("reports", exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        if not results:
            msg = "✅ All user usages are safe. No dict misuse found."
            print(msg)
            f.write(msg + "\n")
        else:
            print("❌ Suspicious user/dict usage found, see log for details.")
            for path, findings in results.items():
                for lineno, msg in findings:
                    line = f"{path}:{lineno}: {msg}"
                    print(line)
                    f.write(line + "\n")
            f.write("\n[End of Report]\n")
    if results:
        exit(1)
