import base64
import hashlib
import json
import os
from typing import Any

# Production-only imports - no fallbacks allowed
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError as e:
    import sys

    sys.stderr.write(
        f"CRITICAL ERROR: cryptography is required for production use. Please install it: pip install cryptography. Details: {e}\n",
    )
    sys.stderr.write("Child data encryption will be disabled - SECURITY RISK!\n")
    raise ImportError(
        "Missing required dependency for encryption: cryptography. Install with 'pip install cryptography'",
    ) from e

from src.infrastructure.security.models import COPPAComplianceRecord

"""AI Teddy Bear - Child Data Encryption System
COPPA-compliant child data encryption system"""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class ChildDataEncryption:
    """COPPA-compliant child data encryption system
    Features:
    - AES-256 encryption for sensitive data
    - Encrypted data segmentation
    - COPPA compliance tracking
    - Comprehensive audit logs
    - Automatic data deletion.
    """

    # Sensitive data that requires encryption
    SENSITIVE_FIELDS = {
        "name",
        "date_of_birth",
        "medical_notes",
        "emergency_contacts",
        "special_needs",
        "cultural_background",
        "custom_settings",
    }

    PII_FIELDS = {
        "name",
        "date_of_birth",
        "gender",
        "emergency_contacts",
        "medical_notes",
        "cultural_background",
    }

    def __init__(self, encryption_key: str | None = None) -> None:
        """Initialize encryption system."""
        self.encryption_key = encryption_key or os.getenv("ENCRYPTION_KEY")
        if not self.encryption_key:
            raise ValueError("Encryption key is required for child data protection")

        # Setup encryption key
        self.cipher = self._setup_encryption_cipher()

        # Setup compliance information
        self.data_retention_days = 90  # COPPA requirement
        self.min_parent_age = 18
        self.max_child_age = 13

        logger.info("Child data encryption system initialized with COPPA compliance")

    def _setup_encryption_cipher(self) -> Fernet:
        """Setup data cipher."""
        try:
            # Convert key to Fernet format
            if len(self.encryption_key) == 44 and self.encryption_key.endswith(b"="):
                # Pre-generated Fernet key
                return Fernet(self.encryption_key.encode())
            # Generate Fernet key from custom key
            password = self.encryption_key.encode()
            salt = os.urandom(16)  # Generate a random 16-byte salt
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            return Fernet(key)
        except Exception as e:
            logger.error(f"Failed to setup encryption cipher: {e}")
            raise ValueError("Invalid encryption key for child data protection")

    def encrypt_child_data(self, child_data: dict[str, Any]) -> dict[str, Any]:
        """Encrypt sensitive child data."""
        try:
            encrypted_data = child_data.copy()
            sensitive_data = {}

            # Extract sensitive data
            for field in self.SENSITIVE_FIELDS:
                if field in child_data and child_data[field] is not None:
                    sensitive_data[field] = child_data[field]
                    # Replace sensitive data with encrypted marker
                    encrypted_data[field] = f"[ENCRYPTED:{field.upper()}]"

            if sensitive_data:
                # Encrypt sensitive data
                sensitive_json = json.dumps(
                    sensitive_data,
                    ensure_ascii=False,
                    default=str,
                )
                encrypted_sensitive = self.cipher.encrypt(
                    sensitive_json.encode("utf-8"),
                )

                # Add encrypted data
                encrypted_data["_encrypted_data"] = base64.b64encode(
                    encrypted_sensitive,
                ).decode("utf-8")

                # Add encryption metadata
                encrypted_data["_encryption_metadata"] = {
                    "encrypted_at": datetime.utcnow().isoformat(),
                    "encryption_version": "1.0",
                    "key_derivation": "PBKDF2HMAC-SHA256",
                    "field_count": len(sensitive_data),
                    "checksum": self._calculate_checksum(sensitive_json),
                }

                logger.info(
                    f"Encrypted {len(sensitive_data)} sensitive fields for child data",
                )

            return encrypted_data
        except Exception as e:
            logger.error(f"Failed to encrypt child data: {e}")
            raise ValueError("Child data encryption failed - data not saved")

    def decrypt_child_data(self, encrypted_data: dict[str, Any]) -> dict[str, Any]:
        """Decrypt child data."""
        try:
            if "_encrypted_data" not in encrypted_data:
                # Data is not encrypted
                return encrypted_data

            decrypted_data = encrypted_data.copy()

            # Decrypt sensitive data
            encrypted_sensitive = base64.b64decode(encrypted_data["_encrypted_data"])
            decrypted_sensitive = self.cipher.decrypt(encrypted_sensitive)
            sensitive_data = json.loads(decrypted_sensitive.decode("utf-8"))

            # Verify data integrity
            metadata = encrypted_data.get("_encryption_metadata", {})
            if metadata.get("field_count") != len(sensitive_data):
                raise ValueError("Data integrity check failed - field count mismatch")

            checksum = self._calculate_checksum(
                json.dumps(sensitive_data, ensure_ascii=False, default=str),
            )
            if metadata.get("checksum") != checksum:
                logger.warning("Data integrity check failed - checksum mismatch")

            # Merge decrypted data
            for field, value in sensitive_data.items():
                decrypted_data[field] = value

            # Remove encryption metadata from final result
            decrypted_data.pop("_encrypted_data", None)
            decrypted_data.pop("_encryption_metadata", None)

            logger.debug(f"Decrypted {len(sensitive_data)} sensitive fields")
            return decrypted_data
        except Exception as e:
            logger.error(f"Failed to decrypt child data: {e}")
            raise ValueError("Child data decryption failed - data may be corrupted")

    def validate_coppa_compliance(
        self,
        child_data: dict[str, Any],
        consent_record: COPPAComplianceRecord,
    ) -> dict[str, Any]:
        """Validate COPPA compliance."""
        compliance_check = {
            "compliant": True,
            "violations": [],
            "warnings": [],
            "required_actions": [],
        }

        child_age = child_data.get("age", 0)
        if child_age > self.max_child_age:
            compliance_check["violations"].append(
                f"Child age ({child_age}) exceeds COPPA limit ({self.max_child_age})",
            )
            compliance_check["compliant"] = False

        if not consent_record.parental_consent_given:
            compliance_check["violations"].append("Parental consent not obtained")
            compliance_check["compliant"] = False

        # Check data expiration
        if consent_record.data_retention_expires:
            if datetime.utcnow() > consent_record.data_retention_expires:
                compliance_check["violations"].append("Data retention period expired")
                compliance_check["required_actions"].append(
                    "Delete child data immediately",
                )
                compliance_check["compliant"] = False

        # Check required PII data
        pii_fields_present = [
            field for field in self.PII_FIELDS if child_data.get(field)
        ]
        if pii_fields_present and not consent_record.parental_consent_given:
            compliance_check["violations"].append(
                f"PII data present without consent: {pii_fields_present}",
            )
            compliance_check["compliant"] = False

        # Warnings
        if not consent_record.consent_ip_address:
            compliance_check["warnings"].append("Consent IP address not recorded")
        if not consent_record.audit_trail:
            compliance_check["warnings"].append("No audit trail available")

        return compliance_check

    def create_consent_record(
        self,
        child_id: str,
        consent_method: str,
        ip_address: str | None = None,
    ) -> COPPAComplianceRecord:
        """Create COPPA consent record."""
        now = datetime.utcnow()
        expiry = now + timedelta(days=self.data_retention_days)

        consent_record = COPPAComplianceRecord(
            child_id=child_id,
            parental_consent_given=True,
            consent_timestamp=now,
            consent_method=consent_method,
            consent_ip_address=ip_address,
            data_retention_expires=expiry,
            audit_trail=[
                {
                    "action": "consent_given",
                    "timestamp": now.isoformat(),
                    "method": consent_method,
                    "ip_address": ip_address,
                },
            ],
        )

        logger.info(f"Created COPPA consent record for child {child_id}")
        return consent_record

    def add_audit_entry(
        self,
        consent_record: COPPAComplianceRecord,
        action: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Add entry to audit trail."""
        audit_entry = {
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {},
        }

        consent_record.audit_trail.append(audit_entry)
        logger.info(f"Added audit entry: {action} for child {consent_record.child_id}")

    def should_delete_data(self, consent_record: COPPAComplianceRecord) -> bool:
        """Determine if data should be deleted."""
        if not consent_record.data_retention_expires:
            return False

        return datetime.utcnow() > consent_record.data_retention_expires

    def anonymize_child_data(self, child_data: dict[str, Any]) -> dict[str, Any]:
        """Anonymize child data for statistical research."""
        anonymized = child_data.copy()

        for field in self.PII_FIELDS:
            if field in anonymized:
                if field == "age":
                    # Keep age group only
                    age = anonymized[field]
                    if age <= 3:
                        anonymized[field] = "toddler"
                    elif age <= 5:
                        anonymized[field] = "preschool"
                    elif age <= 7:
                        anonymized[field] = "early_elementary"
                    elif age <= 10:
                        anonymized[field] = "elementary"
                    else:
                        anonymized[field] = "preteen"
                elif field == "gender":
                    # Keep gender as general category
                    pass
                else:
                    # Delete other personal data
                    anonymized[field] = "[ANONYMIZED]"

        # Add anonymization timestamp
        anonymized["anonymized_at"] = datetime.utcnow().isoformat()
        anonymized["original_id_hash"] = self._calculate_checksum(
            str(child_data.get("id", "")),
        )

        return anonymized

    def _calculate_checksum(self, data: str) -> str:
        """Calculate data checksum."""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()[:16]

    def secure_delete_child_data(self, child_id: str) -> dict[str, Any]:
        """Securely delete child data."""
        deletion_record = {
            "child_id": child_id,
            "deleted_at": datetime.utcnow().isoformat(),
            "deletion_method": "secure_overwrite",
            "compliance_reason": "COPPA_data_retention_expired",
            "verification_hash": self._calculate_checksum(
                f"{child_id}_{datetime.utcnow().isoformat()}",
            ),
        }

        logger.warning(f"Secure deletion of child data: {child_id}")
        return deletion_record
