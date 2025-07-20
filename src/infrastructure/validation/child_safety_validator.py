"""Child Safety Input Validation Service

Provides COPPA-compliant validation specifically focused on child safety,
including age validation, content filtering, and PII protection.
"""

import re
from re import Pattern
from typing import Any
from src.domain.schemas import ValidationResult
from src.domain.exceptions.base_exceptions import ValidationError
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="validation")


