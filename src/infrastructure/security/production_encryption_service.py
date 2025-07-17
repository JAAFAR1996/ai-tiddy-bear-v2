"""
Production Encryption Service

This module provides enterprise-grade encryption services for the AI Teddy Bear
with special focus on child data protection and COPPA compliance.
"""

import base64
import hashlib
import os
import secrets
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Tuple

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class EncryptionType(Enum):
    """Types of encryption supported"""
    AES_256_GCM = "AES-256-GCM"
    FERNET = "FERNET"
    RSA_2048 = "RSA-2048"
    RSA_4096 = "RSA-4096"


class DataClassification(Enum):
    """Data classification levels for different encryption requirements"""
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    CHILD_DATA = "CHILD_DATA"  # Highest protection for children's data


@dataclass
class EncryptionMetadata:
    """Metadata for encrypted data"""
    algorithm: str
    key_id: str
    iv: str
    timestamp: datetime
    classification: DataClassification
    child_safe: bool = True


class ProductionEncryptionService:
    """
    Production-grade encryption service with child data protection
    """
    
    def __init__(self):
        if not CRYPTOGRAPHY_AVAILABLE:
            raise ImportError(
                "cryptography library is required for production encryption"
            )
        
        self._master_key: Optional[bytes] = None
        self._child_data_key: Optional[bytes] = None
        self._initialize_keys()
    
    def _initialize_keys(self) -> None:
        """Initialize encryption keys securely"""
        try:
            # Try to load existing keys or generate new ones
            self._master_key = self._load_or_generate_master_key()
            self._child_data_key = self._derive_child_data_key()
            logger.info("Encryption service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize encryption service: {e}")
            raise
    
    def _load_or_generate_master_key(self) -> bytes:
        """Load existing master key or generate a new one"""
        key_file = os.environ.get("ENCRYPTION_KEY_FILE", ".encryption_key")
        
        if os.path.exists(key_file):
            try:
                with open(key_file, "rb") as f:
                    key = f.read()
                logger.info("Loaded existing master key")
                return key
            except Exception as e:
                logger.warning(f"Failed to load existing key: {e}")
        
        # Generate new master key
        key = Fernet.generate_key()
        
        # Save key securely
        try:
            with open(key_file, "wb") as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Read-write for owner only
            logger.info("Generated and saved new master key")
        except Exception as e:
            logger.warning(f"Failed to save master key: {e}")
        
        return key
    
    def _derive_child_data_key(self) -> bytes:
        """Derive special key for child data encryption"""
        if not self._master_key:
            raise ValueError("Master key not initialized")
        
        # Use PBKDF2 to derive child data key
        salt = b"child_data_salt_teddy_bear_v5"  # Fixed salt for consistency
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(self._master_key)
    
    def encrypt_data(
        self,
        data: bytes,
        classification: DataClassification = DataClassification.INTERNAL,
        encryption_type: EncryptionType = EncryptionType.AES_256_GCM
    ) -> Tuple[bytes, EncryptionMetadata]:
        """
        Encrypt data with specified classification and type
        
        Args:
            data: Raw data to encrypt
            classification: Data classification level
            encryption_type: Type of encryption to use
        
        Returns:
            Tuple of (encrypted_data, metadata)
        """
        try:
            if encryption_type == EncryptionType.AES_256_GCM:
                return self._encrypt_aes_gcm(data, classification)
            elif encryption_type == EncryptionType.FERNET:
                return self._encrypt_fernet(data, classification)
            else:
                raise ValueError(f"Unsupported encryption type: {encryption_type}")
        
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_data(
        self,
        encrypted_data: bytes,
        metadata: EncryptionMetadata
    ) -> bytes:
        """
        Decrypt data using metadata
        
        Args:
            encrypted_data: Encrypted data
            metadata: Encryption metadata
        
        Returns:
            Decrypted data
        """
        try:
            if metadata.algorithm == EncryptionType.AES_256_GCM.value:
                return self._decrypt_aes_gcm(encrypted_data, metadata)
            elif metadata.algorithm == EncryptionType.FERNET.value:
                return self._decrypt_fernet(encrypted_data, metadata)
            else:
                raise ValueError(f"Unsupported algorithm: {metadata.algorithm}")
        
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def _encrypt_aes_gcm(
        self,
        data: bytes,
        classification: DataClassification
    ) -> Tuple[bytes, EncryptionMetadata]:
        """Encrypt using AES-256-GCM"""
        # Use child data key for child data, master key for others
        key = (self._child_data_key 
               if classification == DataClassification.CHILD_DATA 
               else self._master_key)
        
        if not key:
            raise ValueError("Encryption key not available")
        
        # Generate random IV
        iv = os.urandom(12)  # 96-bit IV for GCM
        
        # Create cipher
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        
        # Encrypt data
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        # Combine IV, tag, and ciphertext
        encrypted_data = iv + encryptor.tag + ciphertext
        
        # Create metadata
        metadata = EncryptionMetadata(
            algorithm=EncryptionType.AES_256_GCM.value,
            key_id=hashlib.sha256(key).hexdigest()[:16],
            iv=base64.b64encode(iv).decode(),
            timestamp=datetime.now(),
            classification=classification,
            child_safe=classification == DataClassification.CHILD_DATA
        )
        
        return encrypted_data, metadata
    
    def _decrypt_aes_gcm(
        self,
        encrypted_data: bytes,
        metadata: EncryptionMetadata
    ) -> bytes:
        """Decrypt AES-256-GCM data"""
        # Choose appropriate key
        key = (self._child_data_key 
               if metadata.classification == DataClassification.CHILD_DATA 
               else self._master_key)
        
        if not key:
            raise ValueError("Decryption key not available")
        
        # Extract components
        iv = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]
        
        # Create cipher
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        
        # Decrypt data
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    def _encrypt_fernet(
        self,
        data: bytes,
        classification: DataClassification
    ) -> Tuple[bytes, EncryptionMetadata]:
        """Encrypt using Fernet (simpler but secure)"""
        key = (self._child_data_key 
               if classification == DataClassification.CHILD_DATA 
               else self._master_key)
        
        if not key:
            raise ValueError("Encryption key not available")
        
        # Create Fernet instance
        f = Fernet(base64.urlsafe_b64encode(key))
        
        # Encrypt data
        encrypted_data = f.encrypt(data)
        
        # Create metadata
        metadata = EncryptionMetadata(
            algorithm=EncryptionType.FERNET.value,
            key_id=hashlib.sha256(key).hexdigest()[:16],
            iv="",  # Fernet handles IV internally
            timestamp=datetime.now(),
            classification=classification,
            child_safe=classification == DataClassification.CHILD_DATA
        )
        
        return encrypted_data, metadata
    
    def _decrypt_fernet(
        self,
        encrypted_data: bytes,
        metadata: EncryptionMetadata
    ) -> bytes:
        """Decrypt Fernet data"""
        key = (self._child_data_key 
               if metadata.classification == DataClassification.CHILD_DATA 
               else self._master_key)
        
        if not key:
            raise ValueError("Decryption key not available")
        
        # Create Fernet instance
        f = Fernet(base64.urlsafe_b64encode(key))
        
        # Decrypt data
        return f.decrypt(encrypted_data)
    
    def encrypt_child_data(self, data: bytes) -> Tuple[bytes, EncryptionMetadata]:
        """
        Convenience method for encrypting child data with highest security
        """
        return self.encrypt_data(
            data,
            DataClassification.CHILD_DATA,
            EncryptionType.AES_256_GCM
        )
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
        """
        Hash a password securely using PBKDF2
        
        Args:
            password: Plain text password
            salt: Optional salt (generates new if not provided)
        
        Returns:
            Tuple of (hashed_password, salt)
        """
        if salt is None:
            salt = os.urandom(32)
        
        # Use PBKDF2 with 100,000 iterations
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        hashed = kdf.derive(password.encode())
        
        return (
            base64.b64encode(hashed).decode(),
            base64.b64encode(salt).decode()
        )
    
    def verify_password(self, password: str, hashed: str, salt: str) -> bool:
        """Verify a password against its hash"""
        try:
            salt_bytes = base64.b64decode(salt)
            expected_hash = base64.b64decode(hashed)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt_bytes,
                iterations=100000,
            )
            
            # This will raise an exception if verification fails
            kdf.verify(password.encode(), expected_hash)
            return True
        
        except Exception:
            return False
    
    def get_encryption_status(self) -> Dict[str, Any]:
        """Get current encryption service status"""
        return {
            "initialized": self._master_key is not None,
            "child_data_protection": self._child_data_key is not None,
            "supported_algorithms": [e.value for e in EncryptionType],
            "cryptography_available": CRYPTOGRAPHY_AVAILABLE,
        }


# Global instance for easy access
_encryption_service: Optional[ProductionEncryptionService] = None


def get_encryption_service() -> ProductionEncryptionService:
    """Get global encryption service instance"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = ProductionEncryptionService()
    return _encryption_service


def encrypt_child_data(data: bytes) -> Tuple[bytes, EncryptionMetadata]:
    """Convenience function for encrypting child data"""
    return get_encryption_service().encrypt_child_data(data)


def decrypt_data(encrypted_data: bytes, metadata: EncryptionMetadata) -> bytes:
    """Convenience function for decrypting data"""
    return get_encryption_service().decrypt_data(encrypted_data, metadata)