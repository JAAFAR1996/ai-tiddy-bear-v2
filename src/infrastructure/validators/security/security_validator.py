from src.infrastructure.security.core.security_levels import SecurityLevel
"""Security Validator for AI Teddy Bear v5.

Comprehensive security validation for child safety compliance,
COPPA regulations, and international standards.
"""

import re
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import secrets

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security-validator")


