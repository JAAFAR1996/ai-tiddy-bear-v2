"""Encryption Key Rotation Service

Implements secure key rotation with zero-downtime migration
"""
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import base64
import json
import logging
import os
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")

class KeyRotationService:
    """
    Manages encryption key rotation with the following features:
    - Automatic key rotation every 90 days
    - Dual-key support for zero-downtime rotation
    - Key versioning and metadata tracking
    - Secure key storage and disposal
    - Audit logging for all operations
    """

    def __init__(self, key_storage_path: str = ".keys") -> None:
        self.key_storage_path = Path(key_storage_path)
        self.key_storage_path.mkdir(exist_ok=True, mode=0o700)
        self.rotation_interval_days = 90
        self.max_key_age_days = 180  # Keep old key for migration period
        self.current_key_file = self.key_storage_path / "current_key.json"
        self.previous_key_file = self.key_storage_path / "previous_key.json"

    def generate_new_key(self) -> Dict[str, Any]:
        """Generate a new encryption key with metadata"""
        key = Fernet.generate_key().decode('utf-8')
        key_id = secrets.token_hex(16)
        metadata = {
            "key_id": key_id,
            "key": key,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=self.rotation_interval_days)).isoformat(),
            "version": "1.0",
            "algorithm": "Fernet",
            "rotation_count": self._get_rotation_count() + 1
        }
        logger.info(f"Generated new encryption key with ID: {key_id}")
        return metadata

    def _get_rotation_count(self) -> int:
        """Get the current rotation count"""
        if self.current_key_file.exists():
            try:
                with open(self.current_key_file, 'r') as f:
                    data = json.load(f)
                    return data.get("rotation_count", 0)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Could not read rotation count: {e}")
        return 0

    def rotate_keys(self) -> None:
        """Rotate encryption keys securely"""
        logger.info("Starting key rotation process...")
        new_key_data = self.generate_new_key()

        # Move current key to previous
        if self.current_key_file.exists():
            self.previous_key_file.unlink(missing_ok=True)
            self.current_key_file.rename(self.previous_key_file)
            logger.info("Moved current key to previous key file.")

        # Save new key as current
        with open(self.current_key_file, 'w') as f:
            json.dump(new_key_data, f, indent=4)
        os.chmod(self.current_key_file, 0o600)  # Set strict permissions
        logger.info(f"New key {new_key_data['key_id']} is now the current key.")

    def get_current_key(self) -> Optional[Dict[str, Any]]:
        """Get the current active encryption key"""
        if not self.current_key_file.exists():
            logger.warning("No current key found. Generating a new one.")
            self.rotate_keys()

        with open(self.current_key_file, 'r') as f:
            key_data = json.load(f)
            # Check if key has expired
            expires_at = datetime.fromisoformat(key_data["expires_at"])
            if datetime.utcnow() > expires_at:
                logger.info("Current key has expired. Rotating keys.")
                self.rotate_keys()
                with open(self.current_key_file, 'r') as f_new:
                    return json.load(f_new)
            return key_data

    def get_all_keys(self) -> List[Dict[str, Any]]:
        """Get all available keys (current and previous) for decryption"""
        keys = []
        if self.current_key_file.exists():
            with open(self.current_key_file, 'r') as f:
                keys.append(json.load(f))
        if self.previous_key_file.exists():
            with open(self.previous_key_file, 'r') as f:
                keys.append(json.load(f))
        return keys

    def cleanup_old_keys(self) -> None:
        """Remove old keys that are no longer needed for migration"""
        if self.previous_key_file.exists():
            with open(self.previous_key_file, 'r') as f:
                key_data = json.load(f)
                created_at = datetime.fromisoformat(key_data["created_at"])
                if datetime.utcnow() - created_at > timedelta(days=self.max_key_age_days):
                    logger.info(f"Removing old key {key_data['key_id']}.")
                    self.previous_key_file.unlink()