"""Data Export Formatters
Provides different formatters for exporting child data in various formats.
"""

import csv
import json
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime
from io import BytesIO, StringIO
from typing import Any

from src.infrastructure.logging_config import get_logger

from .types import ExportFormat, ExportMetadata

logger = get_logger(__name__, component="services")


class BaseFormatter:
    """Base class for data formatters."""

    def __init__(self, metadata: ExportMetadata) -> None:
        """Initialize formatter with export metadata."""
        self.metadata = metadata

    def format_data(self, data: dict[str, Any]) -> bytes:
        """Format data into target format."""
        raise NotImplementedError("Subclasses must implement format_data")

    def get_file_extension(self) -> str:
        """Get file extension for this format."""
        raise NotImplementedError("Subclasses must implement get_file_extension")

    def get_mime_type(self) -> str:
        """Get MIME type for this format."""
        raise NotImplementedError("Subclasses must implement get_mime_type")


class JSONFormatter(BaseFormatter):
    """Formats data as JSON."""

    def format_data(self, data: dict[str, Any]) -> bytes:
        """Format data as JSON."""
        try:
            # Add metadata to export
            export_data = {
                "metadata": {
                    "export_timestamp": self.metadata.export_timestamp.isoformat(),
                    "child_id": self.metadata.child_id,
                    "parent_id": self.metadata.parent_id,
                    "data_version": self.metadata.data_version,
                    "total_records": self.metadata.total_records,
                    "coppa_compliance": self.metadata.coppa_compliance_notes,
                    "retention_policy": self.metadata.retention_policy,
                },
                "data": data,
            }
            # Convert datetime objects to ISO format
            json_str = json.dumps(export_data, indent=2, default=self._json_serializer)
            return json_str.encode("utf-8")
        except Exception as e:
            logger.error(f"Error formatting JSON data: {e}")
            raise ValueError(f"Failed to format data as JSON: {e}")

    def _json_serializer(self, obj):
        """Custom JSON serializer for datetime objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def get_file_extension(self) -> str:
        return ".json"

    def get_mime_type(self) -> str:
        return "application/json"


class CSVFormatter(BaseFormatter):
    """Formats data as CSV."""

    def format_data(self, data: dict[str, Any]) -> bytes:
        """Format data as CSV."""
        try:
            output = StringIO()
            # Write metadata header
            output.write("# Child Data Export\n")
            output.write(
                f"# Export Date: {self.metadata.export_timestamp.isoformat()}\n",
            )
            output.write(f"# Child ID: {self.metadata.child_id}\n")
            output.write(f"# Total Records: {self.metadata.total_records}\n")
            output.write("# COPPA Compliant Export\n\n")

            # Process each data category
            for category, records in data.items():
                if not records:
                    continue

                output.write(f"# {category.upper()}\n")

                if isinstance(records, list) and records:
                    # Write CSV for list of records
                    if isinstance(records[0], dict):
                        fieldnames = records[0].keys()
                        writer = csv.DictWriter(output, fieldnames=fieldnames)
                        writer.writeheader()
                        for record in records:
                            # Convert datetime objects to strings
                            csv_record = {}
                            for key, value in record.items():
                                if isinstance(value, datetime):
                                    csv_record[key] = value.isoformat()
                                else:
                                    csv_record[key] = (
                                        str(value) if value is not None else ""
                                    )
                            writer.writerow(csv_record)
                    else:
                        # Simple list
                        writer = csv.writer(output)
                        for record in records:
                            writer.writerow([str(record)])
                elif isinstance(records, dict):
                    # Write key-value pairs
                    writer = csv.writer(output)
                    writer.writerow(["Property", "Value"])
                    for key, value in records.items():
                        if isinstance(value, datetime):
                            value = value.isoformat()
                        writer.writerow([key, str(value) if value is not None else ""])

                output.write("\n")

            return output.getvalue().encode("utf-8")
        except Exception as e:
            logger.error(f"Error formatting CSV data: {e}")
            raise ValueError(f"Failed to format data as CSV: {e}")

    def get_file_extension(self) -> str:
        return ".csv"

    def get_mime_type(self) -> str:
        return "text/csv"


class XMLFormatter(BaseFormatter):
    """Formats data as XML."""

    def format_data(self, data: dict[str, Any]) -> bytes:
        """Format data as XML."""
        try:
            # Create root element
            root = ET.Element("child_data_export")

            # Add metadata
            metadata_elem = ET.SubElement(root, "metadata")
            ET.SubElement(
                metadata_elem,
                "export_timestamp",
            ).text = self.metadata.export_timestamp.isoformat()
            ET.SubElement(metadata_elem, "child_id").text = self.metadata.child_id
            ET.SubElement(metadata_elem, "parent_id").text = self.metadata.parent_id
            ET.SubElement(
                metadata_elem,
                "data_version",
            ).text = self.metadata.data_version
            ET.SubElement(metadata_elem, "total_records").text = str(
                self.metadata.total_records,
            )
            ET.SubElement(
                metadata_elem,
                "retention_policy",
            ).text = self.metadata.retention_policy

            # Add COPPA compliance notes
            coppa_elem = ET.SubElement(metadata_elem, "coppa_compliance")
            for note in self.metadata.coppa_compliance_notes:
                ET.SubElement(coppa_elem, "note").text = note

            # Add data
            data_elem = ET.SubElement(root, "data")
            for category, records in data.items():
                category_elem = ET.SubElement(data_elem, category)

                if isinstance(records, list):
                    for i, record in enumerate(records):
                        record_elem = ET.SubElement(
                            category_elem,
                            "record",
                            {"index": str(i)},
                        )
                        self._add_dict_to_element(record_elem, record)
                elif isinstance(records, dict):
                    self._add_dict_to_element(category_elem, records)
                else:
                    category_elem.text = str(records)

            # Generate XML string
            xml_str = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            return xml_str
        except Exception as e:
            logger.error(f"Error formatting XML data: {e}")
            raise ValueError(f"Failed to format data as XML: {e}")

    def _add_dict_to_element(self, parent: ET.Element, data: dict) -> None:
        """Add dictionary data to XML element."""
        for key, value in data.items():
            if isinstance(value, dict):
                child_elem = ET.SubElement(parent, str(key))
                self._add_dict_to_element(child_elem, value)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    item_elem = ET.SubElement(parent, str(key), {"index": str(i)})
                    if isinstance(item, dict):
                        self._add_dict_to_element(item_elem, item)
                    else:
                        item_elem.text = str(item)
            elif isinstance(value, datetime):
                ET.SubElement(parent, str(key)).text = value.isoformat()
            else:
                ET.SubElement(parent, str(key)).text = (
                    str(value) if value is not None else ""
                )

    def get_file_extension(self) -> str:
        return ".xml"

    def get_mime_type(self) -> str:
        return "application/xml"


class ArchiveFormatter(BaseFormatter):
    """Creates a ZIP archive with multiple formats."""

    def __init__(
        self,
        metadata: ExportMetadata,
        formatters: list[BaseFormatter],
    ) -> None:
        """Initialize with metadata and list of formatters to include."""
        super().__init__(metadata)
        self.formatters = formatters

    def format_data(self, data: dict[str, Any]) -> bytes:
        """Create ZIP archive with multiple format files."""
        try:
            buffer = BytesIO()
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                # Add a README file
                readme_content = self._generate_readme()
                zip_file.writestr("README.txt", readme_content)

                # Add files in different formats
                for formatter in self.formatters:
                    try:
                        formatted_data = formatter.format_data(data)
                        filename = f"child_data_{self.metadata.child_id}{formatter.get_file_extension()}"
                        zip_file.writestr(filename, formatted_data)
                    except Exception as e:
                        logger.warning(
                            f"Failed to add {formatter.__class__.__name__} to archive: {e}",
                        )
                        # Continue with other formats
                        continue

            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Error creating archive: {e}")
            raise ValueError(f"Failed to create data archive: {e}")

    def _generate_readme(self) -> str:
        """Generate README content for the archive."""
        return f"""Child Data Export
================

Export Date: {self.metadata.export_timestamp.isoformat()}
Child ID: {self.metadata.child_id}
Parent ID: {self.metadata.parent_id}
Data Version: {self.metadata.data_version}
Total Records: {self.metadata.total_records}

COPPA Compliance
================
This export complies with the Children's Online Privacy Protection Act (COPPA).
{chr(10).join(self.metadata.coppa_compliance_notes)}

Data Retention Policy
=====================
{self.metadata.retention_policy}

Files Included
==============
- child_data_{self.metadata.child_id}.json - Complete data in JSON format
- child_data_{self.metadata.child_id}.csv - Data in CSV format
- child_data_{self.metadata.child_id}.xml - Data in XML format

For questions about this export, please contact support."""

    def get_file_extension(self) -> str:
        return ".zip"

    def get_mime_type(self) -> str:
        return "application/zip"


class FormatterFactory:
    """Factory for creating data formatters."""

    @staticmethod
    def create_formatter(
        format_type: ExportFormat,
        metadata: ExportMetadata,
    ) -> BaseFormatter:
        """Create appropriate formatter for the given format type."""
        formatters = {
            ExportFormat.JSON: JSONFormatter,
            ExportFormat.CSV: CSVFormatter,
            ExportFormat.XML: XMLFormatter,
        }

        if format_type == ExportFormat.FULL_ARCHIVE:
            # Create archive with all individual formatters
            individual_formatters = [
                JSONFormatter(metadata),
                CSVFormatter(metadata),
                XMLFormatter(metadata),
            ]
            return ArchiveFormatter(metadata, individual_formatters)

        formatter_class = formatters.get(format_type)
        if not formatter_class:
            raise ValueError(f"Unsupported export format: {format_type}")

        return formatter_class(metadata)
