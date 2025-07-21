from src.domain.value_objects.session_status import SessionStatus
"""Session Data Models
Defines core data structures for async session management.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


