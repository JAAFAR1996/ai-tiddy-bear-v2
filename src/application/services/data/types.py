"""Data Export Types and Models
Defines data structures and enums for the data export system.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


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
    formats: list[ExportFormat]
    categories: list[DataCategory]
    date_range_start: datetime | None = None
    date_range_end: datetime | None = None
    include_deleted: bool = False
    anonymize_data: bool = False
    request_id: str | None = None
    created_at: datetime | None = None


@dataclass
class ExportResult:
    """Result of a data export operation."""

    request_id: str
    status: ExportStatus
    created_at: datetime
    completed_at: datetime | None
    file_size_bytes: int | None
    download_url: str | None
    expires_at: datetime | None
    error_message: str | None
    categories_exported: list[DataCategory]
    formats_generated: list[ExportFormat]


@dataclass
class ExportMetadata:
    """Metadata about exported data."""

    export_timestamp: datetime
    child_id: str
    parent_id: str
    data_version: str
    total_records: int
    date_range: dict[str, datetime | None]
    coppa_compliance_notes: list[str]
    retention_policy: str
