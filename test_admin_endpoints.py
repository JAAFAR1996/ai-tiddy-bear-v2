import ast
import os

DUMMY_KEYWORDS = [
    "dummy",
    "mock",
    "fake",
    "placeholder",
    "not implemented",
    "todo",
    "stub",
]
RESULTS = []


def is_dummy_function(node):
    # أي دالة فقط فيها pass أو return None أو raise NotImplementedError أو تعليق dummy
    if not node.body:
        return True
    if len(node.body) == 1:
        stmt = node.body[0]
        # pass
        if isinstance(stmt, ast.Pass):
            return True
        # return ثابت
        if isinstance(stmt, ast.Return) and (
            stmt.value is None
            or isinstance(stmt.value, ast.Constant)
            and stmt.value.value in [None, False, True, [], {}, ""]
        ):
            return True
        # raise NotImplementedError
        if (
            isinstance(stmt, ast.Raise)
            and isinstance(stmt.exc, ast.Call)
            and getattr(stmt.exc.func, "id", "") == "NotImplementedError"
        ):
            return True
        # تعليق فقط
        if (
            hasattr(stmt, "value")
            and isinstance(stmt.value, ast.Constant)
            and any(word in (stmt.value.value or "").lower() for word in DUMMY_KEYWORDS)
        ):
            return True
    # وجود تعليق دمية في جسم الدالة
    for substmt in node.body:
        if isinstance(substmt, ast.Expr) and isinstance(substmt.value, ast.Constant):
            comment = substmt.value.value
            if comment and any(word in comment.lower() for word in DUMMY_KEYWORDS):
                return True
    return False


def scan_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except Exception:
            return
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(
                node, ast.AsyncFunctionDef
            ):
                if is_dummy_function(node):
                    RESULTS.append(
                        {
                            "type": "function",
                            "name": node.name,
                            "file": filepath,
                            "lineno": node.lineno,
                        }
                    )
            elif isinstance(node, ast.ClassDef):
                # كلاس فارغ أو فقط فيه دوال دمية
                if not node.body or all(
                    (
                        isinstance(stmt, ast.Pass)
                        or (
                            isinstance(stmt, ast.FunctionDef)
                            and is_dummy_function(stmt)
                        )
                        or (
                            isinstance(stmt, ast.Expr)
                            and isinstance(stmt.value, ast.Constant)
                            and any(
                                word in (stmt.value.value or "").lower()
                                for word in DUMMY_KEYWORDS
                            )
                        )
                    )
                    for stmt in node.body
                ):
                    RESULTS.append(
                        {
                            "type": "class",
                            "name": node.name,
                            "file": filepath,
                            "lineno": node.lineno,
                        }
                    )


def scan_directory(directory):
    for root, dirs, files in os.walk(directory):
        for fname in files:
            if fname.endswith(".py"):
                scan_file(os.path.join(root, fname))


def print_report():
    if not RESULTS:
        print("✅ No dummy code detected! Your project is production ready.")
        return
    print("\n==== DUMMY CODE REPORT ====\n")
    for entry in RESULTS:
        print(
            f"{entry['type'].upper()}: {entry['name']}  @  {entry['file']}:{entry['lineno']}"
        )
    print(
        f"\nFound {len(RESULTS)} dummy functions/classes. Replace them with production code!"
    )


if __name__ == "__main__":
    # ضع مسار مشروعك هنا (مثلاً: 'src' أو '.')
    PROJECT_PATH = "src"
    scan_directory(PROJECT_PATH)
    print_report()
