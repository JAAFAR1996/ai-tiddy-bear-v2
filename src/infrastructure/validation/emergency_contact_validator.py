"""Emergency Contact Validator

Validates emergency contact information for child safety compliance.
"""

import re
from dataclasses import dataclass
from typing import Any

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="validation")


@dataclass
class EmergencyContact:
    """Emergency contact data structure."""

    name: str
    relationship: str
    phone_number: str
    email: str | None = None
    address: str | None = None
    is_primary: bool = False


class EmergencyContactValidator:
    """Validator for emergency contact information.

    Features:
    - Phone number format validation
    - Relationship validation
    - Contact accessibility validation
    - Duplicate detection
    - Primary contact verification
    """

    def __init__(self) -> None:
        """Initialize emergency contact validator."""
        # Valid relationships for emergency contacts
        self.valid_relationships = {
            "parent",
            "mother",
            "father",
            "guardian",
            "grandparent",
            "grandmother",
            "grandfather",
            "aunt",
            "uncle",
            "family_friend",
            "neighbor",
            "caregiver",
            "babysitter",
        }

        # Phone number patterns for different formats
        self.phone_patterns = [
            # US format
            r"^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$",
            # International
            r"^\+?([1-9]\d{0,3})[-.\s]?(\d{1,4})[-.\s]?(\d{1,4})[-.\s]?(\d{1,9})$",
            # Simple US format
            r"^(\d{3})[-.\s]?(\d{3})[-.\s]?(\d{4})$",
            # 10 digits no formatting
            r"^(\d{10})$",
        ]

        # Compile patterns for performance
        self.compiled_patterns = [
            re.compile(pattern) for pattern in self.phone_patterns
        ]

        logger.info("Emergency contact validator initialized")

    def validate_emergency_contact(
        self,
        contact_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate a single emergency contact.

        Args:
            contact_data: Dictionary containing contact information

        Returns:
            Dict with validation results.
        """
        errors = []
        validated_data = {}

        # Validate name
        name_result = self._validate_name(contact_data.get("name", ""))
        if not name_result["valid"]:
            errors.append(f"Name: {name_result['reason']}")
        else:
            validated_data["name"] = name_result["sanitized_name"]

        # Validate relationship
        relationship_result = self._validate_relationship(
            contact_data.get("relationship", ""),
        )
        if not relationship_result["valid"]:
            errors.append(f"Relationship: {relationship_result['reason']}")
        else:
            validated_data["relationship"] = relationship_result["relationship"]

        # Validate phone number
        phone_result = self._validate_phone_number(contact_data.get("phone_number", ""))
        if not phone_result["valid"]:
            errors.append(f"Phone: {phone_result['reason']}")
        else:
            validated_data["phone_number"] = phone_result["formatted_number"]
            validated_data["phone_country_code"] = phone_result.get("country_code", "")

        # Validate email if provided
        email = contact_data.get("email", "").strip()
        if email:
            email_result = self._validate_email(email)
            if not email_result["valid"]:
                errors.append(f"Email: {email_result['reason']}")
            else:
                validated_data["email"] = email_result["email"]

        # Validate address if provided
        address = contact_data.get("address", "").strip()
        if address:
            address_result = self._validate_address(address)
            if not address_result["valid"]:
                errors.append(f"Address: {address_result['reason']}")
            else:
                validated_data["address"] = address_result["sanitized_address"]

        # Set primary contact flag
        validated_data["is_primary"] = bool(contact_data.get("is_primary", False))

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "validated_data": validated_data,
        }

    def validate_emergency_contacts_list(
        self,
        contacts: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Validate a list of emergency contacts with cross-validation.

        Args:
            contacts: List of contact dictionaries

        Returns:
            Dict with validation results for the entire list.
        """
        if not contacts:
            return {
                "valid": False,
                "reason": "At least one emergency contact is required",
                "errors": ["No emergency contacts provided"],
            }

        if len(contacts) > 5:
            return {
                "valid": False,
                "reason": "Too many emergency contacts (maximum 5)",
                "errors": ["Maximum 5 emergency contacts allowed"],
            }

        validated_contacts = []
        global_errors = []
        phone_numbers = set()
        primary_contacts = 0

        for i, contact in enumerate(contacts):
            # Validate individual contact
            result = self.validate_emergency_contact(contact)
            if not result["valid"]:
                global_errors.extend(
                    [f"Contact {i + 1}: {error}" for error in result["errors"]],
                )
                continue

            validated_contact = result["validated_data"]

            # Check for duplicate phone numbers
            phone = validated_contact["phone_number"]
            if phone in phone_numbers:
                global_errors.append(f"Contact {i + 1}: Duplicate phone number {phone}")
            else:
                phone_numbers.add(phone)

            # Count primary contacts
            if validated_contact.get("is_primary", False):
                primary_contacts += 1

            validated_contacts.append(validated_contact)

        # Validate primary contact rules
        if primary_contacts == 0:
            global_errors.append("At least one contact must be marked as primary")
        elif primary_contacts > 1:
            global_errors.append("Only one contact can be marked as primary")

        # Check for diverse relationships (recommended)
        relationships = {contact["relationship"] for contact in validated_contacts}
        if len(relationships) == 1 and len(validated_contacts) > 1:
            global_errors.append(
                "Recommended: Include contacts with different relationships "
                "for redundancy",
            )

        return {
            "valid": len(global_errors) == 0,
            "errors": global_errors,
            "validated_contacts": validated_contacts,
            "total_contacts": len(validated_contacts),
            "primary_contact_count": primary_contacts,
        }

    def _validate_name(self, name: str) -> dict[str, Any]:
        """Validate emergency contact name."""
        if not name or not isinstance(name, str):
            return {"valid": False, "reason": "Name is required"}

        name = name.strip()
        if len(name) < 2:
            return {
                "valid": False,
                "reason": "Name must be at least 2 characters",
            }

        if len(name) > 100:
            return {
                "valid": False,
                "reason": "Name too long (maximum 100 characters)",
            }

        # Allow letters, spaces, hyphens, apostrophes, and periods
        if not re.match(r"^[a-zA-Z\s\-'.]+$", name):
            return {
                "valid": False,
                "reason": "Name contains invalid characters",
            }

        # Sanitize name
        sanitized_name = " ".join(name.split())  # Normalize whitespace
        sanitized_name = sanitized_name.title()  # Proper case

        return {"valid": True, "sanitized_name": sanitized_name}

    def _validate_relationship(self, relationship: str) -> dict[str, Any]:
        """Validate relationship to child."""
        if not relationship or not isinstance(relationship, str):
            return {"valid": False, "reason": "Relationship is required"}

        relationship = relationship.lower().strip().replace(" ", "_")
        if relationship not in self.valid_relationships:
            return {
                "valid": False,
                "reason": (
                    f"Invalid relationship. Must be one of: "
                    f"{', '.join(sorted(self.valid_relationships))}"
                ),
            }

        return {"valid": True, "relationship": relationship}

    def _validate_phone_number(self, phone: str) -> dict[str, Any]:
        """Validate phone number format."""
        if not phone or not isinstance(phone, str):
            return {"valid": False, "reason": "Phone number is required"}

        # Remove common non-digit characters for validation
        cleaned_phone = re.sub(r"[^\d+]", "", phone)

        # Check against patterns
        for pattern in self.compiled_patterns:
            match = pattern.match(phone)
            if match:
                # Extract components and format consistently
                if phone.startswith("+"):
                    # International format
                    formatted = self._format_international_number(cleaned_phone)
                    country_code = (
                        cleaned_phone[1:2] if len(cleaned_phone) > 10 else None
                    )
                else:
                    # Domestic format - assume US for now
                    formatted = self._format_us_number(cleaned_phone)
                    country_code = "1"

                return {
                    "valid": True,
                    "formatted_number": formatted,
                    "original_number": phone,
                    "country_code": country_code,
                }

        return {
            "valid": False,
            "reason": (
                "Invalid phone number format. Use formats like: "
                "(555) 123-4567, 555-123-4567, or +1-555-123-4567"
            ),
        }

    def _validate_email(self, email: str) -> dict[str, Any]:
        """Validate email address format."""
        if not email or not isinstance(email, str):
            return {
                "valid": False,
                "reason": "Email is required when provided",
            }

        email = email.strip().lower()

        # Basic email regex
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            return {"valid": False, "reason": "Invalid email format"}

        return {"valid": True, "email": email}

    def _validate_address(self, address: str) -> dict[str, Any]:
        """Validate physical address."""
        if not address or not isinstance(address, str):
            return {
                "valid": False,
                "reason": "Address is required when provided",
            }

        address = address.strip()
        if len(address) < 10:
            return {
                "valid": False,
                "reason": "Address too short (minimum 10 characters)",
            }

        if len(address) > 500:
            return {
                "valid": False,
                "reason": "Address too long (maximum 500 characters)",
            }

        # Sanitize address
        sanitized_address = " ".join(address.split())  # Normalize whitespace

        return {"valid": True, "sanitized_address": sanitized_address}

    def _format_us_number(self, cleaned_number: str) -> str:
        """Format US phone number."""
        if len(cleaned_number) == 10:
            return (
                f"({cleaned_number[:3]}) {cleaned_number[3:6]}-" f"{cleaned_number[6:]}"
            )
        if len(cleaned_number) == 11 and cleaned_number[0] == "1":
            return (
                f"+1 ({cleaned_number[1:4]}) {cleaned_number[4:7]}-"
                f"{cleaned_number[7:]}"
            )
        return cleaned_number

    def _format_international_number(self, cleaned_number: str) -> str:
        """Format international phone number."""
        if cleaned_number.startswith("+"):
            return cleaned_number
        return f"+{cleaned_number}"

    def get_contact_accessibility_score(
        self,
        contacts: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Calculate accessibility score for emergency contacts.

        Args:
            contacts: List of validated emergency contacts

        Returns:
            Dict with accessibility analysis.
        """
        if not contacts:
            return {
                "score": 0.0,
                "issues": ["No emergency contacts available"],
                "recommendations": ["Add at least one emergency contact"],
            }

        score = 0.0
        max_score = 100.0
        issues = []
        recommendations = []

        # Base score for having contacts
        score += 20.0 * min(len(contacts), 3) / 3  # Max 20 points for up to 3 contacts

        # Primary contact exists
        primary_contacts = [c for c in contacts if c.get("is_primary", False)]
        if primary_contacts:
            score += 20.0
        else:
            issues.append("No primary contact designated")
            recommendations.append("Designate one contact as primary")

        # Phone number diversity (different area codes)
        phone_prefixes = set()
        for contact in contacts:
            phone = contact.get("phone_number", "")
            if phone:
                # Extract area code/prefix
                digits = re.sub(r"[^\d]", "", phone)
                if len(digits) >= 6:
                    phone_prefixes.add(digits[:3])

        if len(phone_prefixes) > 1:
            score += 15.0

        # Email availability
        contacts_with_email = [c for c in contacts if c.get("email", "").strip()]
        if contacts_with_email:
            score += 10.0 * min(len(contacts_with_email), 2) / 2
        else:
            recommendations.append("Add email addresses for backup communication")

        # Relationship diversity
        relationships = {
            c.get("relationship", "") for c in contacts if c.get("relationship", "")
        }
        if len(relationships) > 1:
            score += 15.0
        elif len(contacts) > 1:
            recommendations.append(
                "Include contacts with different relationships for redundancy",
            )

        # Address availability
        contacts_with_address = [c for c in contacts if c.get("address", "").strip()]
        if contacts_with_address:
            score += 10.0

        # Geographic diversity check (basic)
        if len(contacts_with_address) > 1:
            score += 10.0
        elif len(contacts) > 1:
            recommendations.append(
                "Consider contacts in different locations for emergencies",
            )

        return {
            "score": round(score, 1),
            "max_score": max_score,
            "percentage": round((score / max_score) * 100, 1),
            "issues": issues,
            "recommendations": recommendations,
            "contact_count": len(contacts),
            "contacts_with_email": len(contacts_with_email),
            "relationship_diversity": len(relationships),
        }
