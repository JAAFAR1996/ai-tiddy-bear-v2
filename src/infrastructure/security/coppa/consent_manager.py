"""COPPA-Compliant Real Parental Verification System
This module implements the 4 FTC-approved verification methods for COPPA compliance:
1. Credit card verification with $0.01 charge
2. Government ID verification with AI/manual review
3. Knowledge-based authentication (KBA)
4. Digital signature with legal validation.
"""

import hashlib
import re
import secrets
from datetime import datetime, timedelta
from enum import Enum
from src.application.services.consent.consent_models import VerificationMethod, VerificationStatus
from typing import Any

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


