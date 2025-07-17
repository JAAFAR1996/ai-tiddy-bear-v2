"""Provides services for exporting child data in a COPPA-compliant manner.

This service handles requests for data export, supporting various formats
(JSON, CSV, XML, PDF) and granular data category selection. It ensures
secure file generation, storage, and automatic cleanup, while maintaining
audit logs for compliance.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from src.infrastructure.logging_config import get_logger

from .data_export.formatters import DataExportFormatters
from .data_export.types import (
    EXPORT_LIMITS,
    ChildProfile,
    ConversationData,
    ExportRequest,
    ExportResult,
    ExportStatus,
    SafetyEvent,
    UsageStatistics,
)


class DataExportService:
    """COPPA-compliant data export service for child data."""

    def __init__(
        self,
        storage_path: str = "exports",
        logger: logging.Logger = get_logger(
            __name__, component="data_export_service"
        ),
    ) -> None:
        """Initializes the data export service.

        Args:
            storage_path: The path where exported files will be stored.
            logger: Logger instance for logging service operations.

        """
        self.storage_path = storage_path
        self.formatters = DataExportFormatters(storage_path)
        self.active_exports: dict[str, ExportResult] = {}
        self.logger = logger
        self.logger.info(
            f"Data export service initialized with storage path: {storage_path}",
        )

    def _sanitize_data_for_export(
        self, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Recursively sanitizes sensitive data fields before export to prevent PII exposure.

        Args:
            data: The dictionary containing data to be sanitized.

        Returns:
            A new dictionary with sensitive fields sanitized.

        """
        sanitized_data = {}
        for key, value in data.items():
            if key in [
                "name",
                "text",
                "description",
            ]:  # Fields potentially containing PII
                if isinstance(value, str):
                    # Replace with a placeholder
                    sanitized_data[key] = "[REDACTED]"
                else:
                    sanitized_data[key] = value  # Keep non-string values as is
            elif isinstance(value, dict):
                sanitized_data[key] = self._sanitize_data_for_export(value)
            elif isinstance(value, list):
                sanitized_data[key] = [
                    (
                        self._sanitize_data_for_export(item)
                        if isinstance(item, dict)
                        else item
                    )
                    for item in value
                ]
            else:
                sanitized_data[key] = value
        return sanitized_data

    def request_export(self, request: ExportRequest) -> ExportResult:
        """Requests a data export for a child.

        Args:
            request: The export request with configuration.

        Returns:
            An ExportResult object with operation details.

        """
        export_id = str(uuid.uuid4())
        result = ExportResult(
            export_id=export_id,
            request=request,
            status=ExportStatus.PENDING,
            created_at=datetime.utcnow(),
        )
        self.active_exports[export_id] = result

        try:
            self._validate_export_request(request)
            # In a real scenario, this would trigger an async task
            # For now, we'll simulate the export process
            exported_file_path = self._simulate_export(request)
            result.status = ExportStatus.COMPLETED
            result.file_path = exported_file_path
            result.completed_at = datetime.utcnow()
            self.logger.info(
                f"Export {export_id} completed: {exported_file_path}"
            )
        except Exception as e:
            result.status = ExportStatus.FAILED
            result.error_message = str(e)
            result.completed_at = datetime.utcnow()
            self.logger.error(f"Export {export_id} failed: {e}", exc_info=True)

        return result

    def get_export_status(self, export_id: str) -> ExportResult | None:
        """Retrieves the status of an ongoing or completed export operation.

        Args:
            export_id: The ID of the export operation.

        Returns:
            The ExportResult object, or None if the export ID is not found.

        """
        return self.active_exports.get(export_id)

    def _validate_export_request(self, request: ExportRequest) -> None:
        """Validates the export request against predefined limits and rules.

        Args:
            request: The export request to validate.

        Raises:
            ValueError: If the request is invalid.

        """
        if request.end_date < request.start_date:
            raise ValueError("End date cannot be before start date.")

        if (request.end_date - request.start_date).days > EXPORT_LIMITS[
            "max_days_range"
        ]:
            raise ValueError(
                f"Date range exceeds maximum allowed {EXPORT_LIMITS['max_days_range']} days.",
            )

        if len(request.data_categories) > EXPORT_LIMITS["max_categories"]:
            raise ValueError(
                f"Too many data categories requested. Max: {EXPORT_LIMITS['max_categories']}.",
            )

    def _simulate_export(self, request: ExportRequest) -> str:
        """Simulates the data export process and returns a dummy file path.

        Args:
            request: The export request.

        Returns:
            A dummy file path for the exported data.

        """
        # In a real system, this would fetch data from various sources
        # (e.g., database, file storage) and format it.
        dummy_data = {
            "child_profile": ChildProfile(
                child_id=request.child_id, name="Test Child"
            ),
            "conversations": [
                ConversationData(timestamp=datetime.utcnow(), text="Hello"),
                ConversationData(
                    timestamp=datetime.utcnow(), text="How are you?"
                ),
            ],
            "safety_events": [
                SafetyEvent(
                    timestamp=datetime.utcnow(), description="Minor flag"
                ),
            ],
            "usage_statistics": UsageStatistics(total_interactions=100),
        }

        # Sanitize data before passing to formatter
        sanitized_dummy_data = self._sanitize_data_for_export(dummy_data)

        # Use the formatter to save the dummy data
        file_path = self.formatters.format_and_save(
            request.export_format,
            request.child_id,
            sanitized_dummy_data,
        )
        return file_path
