class SecurityPatterns:
    SQLI_PATTERNS = [
        r"(?i)(union\s+select)",
        r"(?i)(drop\s+table)",
        r"(?i)(insert\s+into)",
        r"(?i)(delete\s+from)",
        r"(?i)(update\s+\w+\s+set)",
        r"(?i)(;--)",
        r"(?i)(or\s+\d+=\d+)",
    ]
    XSS_PATTERNS = [
        r"(?i)<script.*?>",
        r"(?i)on\w+\s*=",
        r"(?i)javascript:",
        r"(?i)document\.cookie",
    ]
    # Expand as needed
