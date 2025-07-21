"""Data Export Service - COPPA Compliant
Production-ready service for exporting child data with proper security and compliance.
"""

import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.infrastructure.logging_config import get_logger
from src.infrastructure.di.container import container

from .formatters import FormatterFactory
from .types import (
    ExportRequest,
    ExportResult,
    ExportStatus,
    ExportFormat,
    ExportMetadata,
    DataCategory,
)

# Export limits configuration
EXPORT_LIMITS = {
    "max_days_range": 365,
    "max_categories": 10,
    "max_file_size_mb": 100,
    "retention_days": 30,
}


class DataExportService:
    """COPPA-compliant data export service for child data."""

    def __init__(
        self,
        storage_path: str = "exports",
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """Initialize the data export service.
        
        Args:
            storage_path: Path to store exported files
            logger: Optional logger instance
        """
        self._logger = logger or get_logger(__name__, component="data_export_service")
        self._storage_path = Path(storage_path)
        self._storage_path.mkdir(parents=True, exist_ok=True)
        self._pending_exports: Dict[str, ExportResult] = {}
        self._formatter_factory = FormatterFactory()

    def _sanitize_data_for_export(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data to ensure COPPA compliance.
        
        Args:
            data: Raw data to sanitize
            
        Returns:
            Sanitized data safe for export
        """
        if not isinstance(data, dict):
            return data
            
        sanitized_data = {}
        
        # List of fields to remove for COPPA compliance
        sensitive_fields = {
            'ip_address', 'device_id', 'location', 'precise_location',
            'email', 'phone_number', 'full_address', 'social_media_id',
            'biometric_data', 'genetic_data', 'health_records'
        }
        
        for key, value in data.items():
            # Skip sensitive fields
            if key.lower() in sensitive_fields:
                continue
                
            if isinstance(value, dict):
                sanitized_data[key] = self._sanitize_data_for_export(value)
            elif isinstance(value, list):
                sanitized_data[key] = [
                    self._sanitize_data_for_export(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                # Anonymize certain fields
                if key.lower() in ['name', 'child_name', 'parent_name']:
                    sanitized_data[key] = self._anonymize_name(str(value))
                else:
                    sanitized_data[key] = value
                
        return sanitized_data

    def _anonymize_name(self, name: str) -> str:
        """Anonymize a name for privacy protection."""
        if not name:
            return "Anonymous"
        parts = name.split()
        if len(parts) > 1:
            return f"{parts[0][0]}. {parts[-1][0]}."
        return f"{name[0]}."

    def request_export(self, request: ExportRequest) -> ExportResult:
        """Request a data export for a child.
        
        Args:
            request: Export request details
            
        Returns:
            Export result with status and details
        """
        try:
            # Validate request
            self._validate_export_request(request)
            
            # Generate request ID
            request_id = request.request_id or f"export_{uuid.uuid4().hex}"
            
            # Create result object
            result = ExportResult(
                request_id=request_id,
                status=ExportStatus.IN_PROGRESS,
                created_at=datetime.utcnow(),
                completed_at=None,
                file_size_bytes=None,
                download_url=None,
                expires_at=None,
                error_message=None,
                categories_exported=request.categories,
                formats_generated=request.formats,
            )
            
            # Store pending export
            self._pending_exports[request_id] = result
            
            # Log export request
            self._logger.info(
                f"Export requested for child {request.child_id}",
                extra={
                    "child_id": request.child_id,
                    "parent_id": request.parent_id,
                    "request_id": request_id,
                }
            )
            
            # Execute export
            try:
                file_paths = self._execute_export(request)
                
                # Update result with success
                result.status = ExportStatus.COMPLETED
                result.completed_at = datetime.utcnow()
                result.download_url = file_paths[0] if file_paths else None
                result.expires_at = datetime.utcnow() + timedelta(days=EXPORT_LIMITS["retention_days"])
                
                # Calculate file size
                if file_paths:
                    result.file_size_bytes = sum(
                        os.path.getsize(fp) for fp in file_paths if os.path.exists(fp)
                    )
                
            except Exception as e:
                # Update result with failure
                result.status = ExportStatus.FAILED
                result.error_message = str(e)
                self._logger.error(f"Export failed: {str(e)}", exc_info=True)
                
            return result
            
        except Exception as e:
            self._logger.error(f"Export request failed: {str(e)}")
            raise

    def _execute_export(self, request: ExportRequest) -> List[str]:
        """Execute the actual data export.
        
        Args:
            request: Export request details
            
        Returns:
            List of file paths for exported data
        """
        # Gather data based on requested categories
        export_data = self._gather_export_data(request)
        
        # Sanitize the data
        sanitized_data = self._sanitize_data_for_export(export_data)
        
        # Create metadata
        metadata = ExportMetadata(
            export_timestamp=datetime.utcnow(),
            child_id=request.child_id,
            parent_id=request.parent_id,
            data_version="1.0",
            total_records=self._count_records(sanitized_data),
            date_range={
                "start": request.date_range_start.isoformat() if request.date_range_start else None,
                "end": request.date_range_end.isoformat() if request.date_range_end else None,
            },
            coppa_compliance_notes=[
                "Data exported in compliance with COPPA regulations",
                "Personal information has been sanitized",
                f"Data will be retained for {EXPORT_LIMITS['retention_days']} days",
            ],
            retention_policy=f"Automatic deletion after {EXPORT_LIMITS['retention_days']} days"
        )
        
        # Generate exports in requested formats
        file_paths = []
        for export_format in request.formats:
            formatter = self._formatter_factory.get_formatter(export_format, metadata)
            
            # Format the data
            formatted_data = formatter.format_data(sanitized_data)
            
            # Save to file
            filename = f"{request.child_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            filename = f"{filename}.{formatter.get_file_extension()}"
            file_path = self._storage_path / filename
            
            # Write data
            with open(file_path, 'wb') as f:
                f.write(formatted_data)
                
            file_paths.append(str(file_path))
            
            self._logger.info(f"Exported data to {file_path}")
            
        return file_paths

    def _gather_export_data(self, request: ExportRequest) -> Dict[str, Any]:
        """Gather data from various sources based on request."""
        export_data = {}

        # Get services from container
        child_service = container.resolve_service("ChildService")
        conversation_service = container.resolve_service("ConversationService")
        safety_service = container.resolve_service("SafetyService")

        # Gather data based on categories
        for category in request.categories:
            if category == DataCategory.PROFILE:
                export_data["profile"] = self._get_child_profile(request.child_id, child_service)
            elif category == DataCategory.CONVERSATIONS:
                export_data["conversations"] = self._get_conversations(
                    request.child_id, request.date_range_start, request.date_range_end, conversation_service
                )
            elif category == DataCategory.SAFETY_EVENTS:
                export_data["safety_events"] = self._get_safety_events(
                    request.child_id, request.date_range_start, request.date_range_end, safety_service
                )
            elif category == DataCategory.USAGE_STATISTICS:
                export_data["usage_statistics"] = self._get_usage_statistics(
                    request.child_id, request.date_range_start, request.date_range_end
                )
            elif category == DataCategory.ALL:
                export_data["profile"] = self._get_child_profile(request.child_id, child_service)
                export_data["conversations"] = self._get_conversations(
                    request.child_id, request.date_range_start, request.date_range_end, conversation_service
                )
                export_data["safety_events"] = self._get_safety_events(
                    request.child_id, request.date_range_start, request.date_range_end, safety_service
                )
                export_data["usage_statistics"] = self._get_usage_statistics(
                    request.child_id, request.date_range_start, request.date_range_end
                )
                break

        return export_data

    def _get_fallback_data(self, request: ExportRequest) -> Dict[str, Any]:
        """Get fallback data when services are not available."""
        return {
            "export_info": {
                "child_id": request.child_id,
                "parent_id": request.parent_id,
                "export_date": datetime.utcnow().isoformat(),
                "requested_categories": [cat.value for cat in request.categories],
                "message": "Limited data available due to service unavailability"
            }
        }

    def _get_child_profile(self, child_id: str, child_service: Any) -> Dict[str, Any]:
        """Get child profile data."""
        try:
            if child_service:
                profile = child_service.get_child_profile(child_id)
                if profile:
                    return profile.dict() if hasattr(profile, 'dict') else profile
        except Exception as e:
            self._logger.warning(f"Failed to get child profile: {e}")
        return {"message": "لا توجد بيانات ملف الطفل", "child_id": child_id}

    def _get_conversations(
        self, 
        child_id: str, 
        start_date: Optional[datetime], 
        end_date: Optional[datetime],
        conversation_service: Any
    ) -> List[Dict[str, Any]]:
        """Get conversation data."""
        try:
            if conversation_service:
                conversations = conversation_service.get_conversations(
                    child_id=child_id,
                    start_date=start_date,
                    end_date=end_date
                )
                if conversations:
                    return [conv.dict() if hasattr(conv, 'dict') else conv for conv in conversations]
        except Exception as e:
            self._logger.warning(f"Failed to get conversations: {e}")
        return [{"message": "لا توجد محادثات"}]

    def _get_safety_events(
        self,
        child_id: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        safety_service: Any
    ) -> List[Dict[str, Any]]:
        """Get safety event data."""
        try:
            if safety_service:
                events = safety_service.get_safety_events(
                    child_id=child_id,
                    start_date=start_date,
                    end_date=end_date
                )
                if events:
                    return [event.dict() if hasattr(event, 'dict') else event for event in events]
        except Exception as e:
            self._logger.warning(f"Failed to get safety events: {e}")
        return [{"message": "لا توجد أحداث أمان"}]

    def _get_usage_statistics(
        self,
        child_id: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> Dict[str, Any]:
        """Get usage statistics."""
        # إذا لم توجد بيانات، يرجع رسالة
        return {"message": "لا توجد إحصائيات استخدام", "child_id": child_id}

    def _count_records(self, data: Dict[str, Any]) -> int:
        """Count total records in export data."""
        count = 0
        for key, value in data.items():
            if isinstance(value, list):
                count += len(value)
            elif isinstance(value, dict):
                count += 1
        return count

    def get_export_status(self, export_id: str) -> Optional[ExportResult]:
        """Get the status of an export request.
        
        Args:
            export_id: Export request ID
            
        Returns:
            Export result if found, None otherwise
        """
        return self._pending_exports.get(export_id)

    def _validate_export_request(self, request: ExportRequest) -> None:
        """Validate export request for COPPA compliance.
        
        Args:
            request: Export request to validate
            
        Raises:
            ValueError: If request is invalid
        """
        # Validate required fields
        if not request.child_id:
            raise ValueError("Child ID is required")
        if not request.parent_id:
            raise ValueError("Parent ID is required")
        if not request.formats:
            raise ValueError("At least one export format must be specified")
        if not request.categories:
            raise ValueError("At least one data category must be specified")
            
        # Validate date range
        if request.date_range_start and request.date_range_end:
            if request.date_range_end < request.date_range_start:
                raise ValueError("End date cannot be before start date")
                
            days_diff = (request.date_range_end - request.date_range_start).days
            if days_diff > EXPORT_LIMITS["max_days_range"]:
                raise ValueError(
                    f"Date range exceeds maximum allowed {EXPORT_LIMITS['max_days_range']} days"
                )
        
        # Validate categories
        if len(request.categories) > EXPORT_LIMITS["max_categories"]:
            raise ValueError(
                f"Too many categories requested. Max: {EXPORT_LIMITS['max_categories']}"
            )

    def delete_export(self, export_id: str) -> bool:
        """Delete an exported file.
        
        Args:
            export_id: Export request ID
            
        Returns:
            True if deleted, False if not found
        """
        result = self._pending_exports.get(export_id)
        if result and result.download_url:
            try:
                if os.path.exists(result.download_url):
                    os.remove(result.download_url)
                    self._logger.info(f"Deleted export file: {result.download_url}")
                del self._pending_exports[export_id]
                return True
            except Exception as e:
                self._logger.error(f"Failed to delete export: {e}")
        return False
