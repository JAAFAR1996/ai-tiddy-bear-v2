from src.domain.interfaces.encryption_interface import (
    EncryptionServiceInterface,
    NullEncryptionService,
    SecureFieldInterface,
)


class EncryptedFieldError(Exception):
    """Exception raised for errors in EncryptedField operations."""

    def __init__(self, value_type: type):
        super().__init__(f"Unsupported value type for encryption: {value_type}")


class EncryptedField(SecureFieldInterface[str | int | float | bool | list | dict]):
    """Value object for encrypted storage of sensitive data.

    Provides transparent encryption and decryption for HIPAA/COPPA compliance.
    Uses dependency injection for encryption service to maintain clean architecture.

    Args:
        value (str | int | float | bool | list | dict): The value to be encrypted. Should be serializable.
        encryption_service (EncryptionServiceInterface, optional): Service to handle encryption operations. Defaults to NullEncryptionService.

    Raises:
        EncryptedFieldError: If value is not serializable (see note below).

    Note:
        Only basic types (str, int, float, bool, list, dict) are supported for serialization. For complex types, extend serialization logic as needed.
    """

    def __init__(
        self,
        value: str | int | float | bool | list | dict,
        encryption_service: EncryptionServiceInterface = None,
    ) -> None:
        self._encryption_service = encryption_service or NullEncryptionService()
        self._original_value = value
        self._encrypted_data = self._serialize_and_encrypt(value)
        self._is_encrypted = self._encryption_service.is_available()

    def _serialize_and_encrypt(
        self, value: str | int | float | bool | list | dict
    ) -> str:
        """Serialize the value and encrypt it.

        Args:
            value (str | int | float | bool | list | dict): The value to serialize and encrypt.

        Returns:
            str: Encrypted string representation of the value.
        """
        if value is None:
            return ""
        if isinstance(value, str):
            serialized = value
        elif isinstance(value, int | float | bool):
            serialized = str(value)
        elif isinstance(value, list | dict):
            # For complex types, use string representation (consider using JSON
            # for production)
            serialized = str(value)
        else:
            # If you need to support more types, extend here
            raise EncryptedFieldError(type(value))
        return self._encryption_service.encrypt(serialized)

    def get_value(self) -> str | int | float | bool | list | dict | None:
        """Get the decrypted value.

        Returns:
            str | int | float | bool | list | dict | None: The decrypted value, or None if not set.
        """
        if not self._encrypted_data:
            return None
        if self._is_encrypted:
            decrypted_str = self._encryption_service.decrypt(self._encrypted_data)
            return self._deserialize_value(decrypted_str)
        return self._deserialize_value(self._encrypted_data)

    def _deserialize_value(
        self, serialized: str
    ) -> str | int | float | bool | list | dict | None:
        """Deserialize the string back to the original type.

        Args:
            serialized (str): The serialized string value.

        Returns:
            str | int | float | bool | list | dict | None: The deserialized value.

        Note:
            For production, implement robust deserialization logic (e.g., using type metadata or JSON). Currently, returns the string as-is for compatibility and safety.
        """
        # For production, implement robust deserialization if you need to restore original types. This is left as-is to avoid unsafe eval or guessing.
        return serialized

    def __hash__(self):
        return hash((self._encrypted_data, self._is_encrypted))
