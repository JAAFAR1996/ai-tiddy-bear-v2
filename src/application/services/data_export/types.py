"""from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any.
"""

"""Data Export Types and Models
Defines data structures and enums for the data export system."""


class ExportFormat(Enum):
    """Supported export formats."""

    JSON = "json"
    CSV = "csv"
    XML = "xml"
    PDF = "pdf"
    FULL_ARCHIVE = "full_archive"  # ZIP with all formats


class DataCategory(Enum):
    """Categories of data that can be exported."""

    PROFILE = "profile"
    CONVERSATIONS = "conversations"
    SAFETY_EVENTS = "safety_events"
    USAGE_STATISTICS = "usage_statistics"
    MEDICAL_NOTES = "medical_notes"
    EMERGENCY_CONTACTS = "emergency_contacts"
    PARENTAL_CONSENTS = "parental_consents"
    ALL = "all"


class ExportStatus(Enum):
    """Export request status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExportRequest:
    """Data export request with configuration."""

    child_id: str
    parent_id: str
    formats: List[ExportFormat]
    categories: List[DataCategory]
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    include_deleted: bool = False
    anonymize_data: bool = False
    request_id: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class ExportResult:
    """Result of a data export operation."""

    request_id: str
    status: ExportStatus
    created_at: datetime
    completed_at: Optional[datetime]
    file_size_bytes: Optional[int]
    download_url: Optional[str]
    expires_at: Optional[datetime]
    error_message: Optional[str]
    categories_exported: List[DataCategory]
    formats_generated: List[ExportFormat]


@dataclass
class ExportMetadata:
    """Metadata about exported data."""

    export_timestamp: datetime
    child_id: str
    parent_id: str
    data_version: str
    total_records: int
    date_range: Dict[str, Optional[datetime]]
    coppa_compliance_notes: List[str]
    retention_policy: str
