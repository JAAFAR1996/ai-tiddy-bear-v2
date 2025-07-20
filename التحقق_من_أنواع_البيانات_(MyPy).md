## التحقق من أنواع البيانات (MyPy)
```bash
mypy src/ --exclude .venv|venv|__pycache__|build|dist|.mypy_cache|node_modules|.git
```

_Error or No results._
```
/bin/sh: 1: venv: not found
/bin/sh: 1: __pycache__: Permission denied
/bin/sh: 1: build: not found
/bin/sh: 1: .mypy_cache: not found
/bin/sh: 1: dist: not found
/bin/sh: 1: .git: not found
/bin/sh: 1: node_modules: Permission denied

```

⏱️ الوقت المستغرق: 7.22 ثانية


---

