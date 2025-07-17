"""
Provides services for reporting, tracking, and resolving incidents.

This service allows for the creation of incident reports, retrieval of incident
details, and resolution of incidents. It helps in maintaining a record of
system issues and their resolutions, contributing to system reliability and
accountability.
"""

from datetime import datetime
from typing import Any, Dict


class IncidentService:
    """Service for reporting, tracking, and resolving incidents."""

    def __init__(self) -> None:
        """Initializes the incident service."""
        self.incidents: list[Dict[str, Any]] = []

    async def report_incident(
            self, incident_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reports a new incident.

        Args:
            incident_details: A dictionary containing details about the incident.

        Returns:
            A dictionary representing the reported incident.
        """
        incident_id = f"inc_{len(self.incidents) + 1}"
        incident = {
            "id": incident_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "reported",
            **incident_details,
        }
        self.incidents.append(incident)
        return incident

    async def get_incident(self, incident_id: str) -> Dict[str, Any] | None:
        """
        Retrieves details of a specific incident.

        Args:
            incident_id: The ID of the incident to retrieve.

        Returns:
            A dictionary representing the incident, or None if not found.
        """
        for inc in self.incidents:
            if inc.get("id") == incident_id:
                return inc
        return None

    async def resolve_incident(
        self, incident_id: str, resolution_details: Dict[str, Any]
    ) -> Dict[str, Any] | None:
        """
        Resolves an existing incident.

        Args:
            incident_id: The ID of the incident to resolve.
            resolution_details: A dictionary containing details about the resolution.

        Returns:
            A dictionary representing the resolved incident, or None if not found.
        """
        for inc in self.incidents:
            if inc.get("id") == incident_id:
                inc["status"] = "resolved"
                inc["resolved_at"] = datetime.utcnow().isoformat()
                inc["resolution_details"] = resolution_details
                return inc
        return None
