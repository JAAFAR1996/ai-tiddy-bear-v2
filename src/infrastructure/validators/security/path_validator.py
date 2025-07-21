"""Path security validator."""
import os
from pathlib import Path

class SecurityError(Exception):
    """Security validation error."""
    pass

class PathValidator:
    """Validate paths for security issues."""
    
    def validate(self, path: str) -> bool:
        """Validate path is safe."""
        try:
            # Check for path traversal
            normalized = os.path.normpath(path)
            if '..' in normalized or normalized.startswith('/'):
                raise SecurityError("Path traversal detected")
            return True
        except Exception as e:
            raise SecurityError(f"Invalid path: {e}")
