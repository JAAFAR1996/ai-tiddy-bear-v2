"""
Request Signing Service
Provides cryptographic request signing and validation for child safety.
Implements HMAC-based signatures with replay attack protection.
"""

import base64
import hashlib
import hmac
import json
import secrets
import time
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class SignatureAlgorithm(Enum):
    """Supported signature algorithms."""

    HMAC_SHA256 = "hmac-sha256"
    HMAC_SHA512 = "hmac-sha512"


class RequestSecurityLevel(Enum):
    """Security levels for different request types."""

    CHILD_INTERACTION = "child_interaction"
    # Highest security for child requests
    PARENT_ACCESS = "parent_access"  # High security for parent requests
    ADMIN_OPERATION = "admin_operation"  # Maximum security for admin requests
    PUBLIC_API = "public_api"  # Basic security for public endpoints


@dataclass
class SignatureConfiguration:
    """Configuration for request signing."""

    algorithm: SignatureAlgorithm
    key_id: str
    secret_key: bytes
    timestamp_tolerance_seconds: int
    include_body_hash: bool
    include_query_params: bool
    require_nonce: bool
    max_nonce_age_seconds: int


@dataclass
class SignatureValidationResult:
    """Result of signature validation."""

    valid: bool
    reason: Optional[str] = None
    timestamp: Optional[datetime] = None
    key_id: Optional[str] = None
    algorithm: Optional[str] = None
    security_flags: List[str] = None

    def __post_init__(self):
        if self.security_flags is None:
            self.security_flags = []


class RequestSigningService:
    """
    Enterprise-grade request signing service for child safety.
    Features:
    - HMAC-based request signatures
    - Replay attack prevention
    - Timestamp validation
    - Nonce tracking
    - Child-specific security levels
    - Key rotation support
    """

    def __init__(
        self,
        default_level: RequestSecurityLevel = RequestSecurityLevel.CHILD_INTERACTION,
    ) -> None:
        """Initialize request signing service."""
        self.default_level = default_level
        self.configurations = self._initialize_configurations()
        self.nonce_cache: Dict[str, datetime] = {}
        self.signature_cache: Dict[str, datetime] = {}
        self.max_cache_size = 10000
        self.cache_cleanup_interval = timedelta(hours=1)
        self.last_cleanup = datetime.utcnow()
        logger.info(
            f"Request signing service initialized with {default_level.value} level"
        )

    def _initialize_configurations(
        self,
    ) -> Dict[RequestSecurityLevel, SignatureConfiguration]:
        """Initialize signature configurations for different security levels."""
        # In production, these keys should come from secure key management
        base_key = b"ai_teddy_signing_key_2025"
        return {
            RequestSecurityLevel.CHILD_INTERACTION: SignatureConfiguration(
                algorithm=SignatureAlgorithm.HMAC_SHA512,
                key_id="child_interaction_v1",
                secret_key=base_key + b"_child",
                timestamp_tolerance_seconds=60,  # 1 minute tolerance
                include_body_hash=True,
                include_query_params=True,
                require_nonce=True,
                max_nonce_age_seconds=300,  # 5 minutes
            ),
            RequestSecurityLevel.PARENT_ACCESS: SignatureConfiguration(
                algorithm=SignatureAlgorithm.HMAC_SHA256,
                key_id="parent_access_v1",
                secret_key=base_key + b"_parent",
                timestamp_tolerance_seconds=300,  # 5 minutes tolerance
                include_body_hash=True,
                include_query_params=True,
                require_nonce=True,
                max_nonce_age_seconds=900,  # 15 minutes
            ),
            RequestSecurityLevel.ADMIN_OPERATION: SignatureConfiguration(
                algorithm=SignatureAlgorithm.HMAC_SHA512,
                key_id="admin_operation_v1",
                secret_key=base_key + b"_admin",
                timestamp_tolerance_seconds=30,  # 30 seconds tolerance
                include_body_hash=True,
                include_query_params=True,
                require_nonce=True,
                max_nonce_age_seconds=180,  # 3 minutes
            ),
            RequestSecurityLevel.PUBLIC_API: SignatureConfiguration(
                algorithm=SignatureAlgorithm.HMAC_SHA256,
                key_id="public_api_v1",
                secret_key=base_key + b"_public",
                timestamp_tolerance_seconds=600,  # 10 minutes tolerance
                include_body_hash=False,
                include_query_params=False,
                require_nonce=False,
                max_nonce_age_seconds=0,
            ),
        }

    def sign_request(
        self,
        method: str,
        url: str,
        body: Optional[bytes] = None,
        headers: Optional[Dict[str, str]] = None,
        level: Optional[RequestSecurityLevel] = None,
        custom_claims: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """
        Sign an HTTP request with cryptographic signature.
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full request URL
            body: Request body bytes
            headers: Request headers
            level: Security level to apply
            custom_claims: Additional claims to include in signature
        Returns:
            Dict of headers to add to the request
        """
        level = level or self.default_level
        config = self.configurations[level]
        headers = headers or {}
        
        # Generate timestamp and nonce
        timestamp = int(time.time())
        nonce = self._generate_nonce() if config.require_nonce else None
        
        # Build signature payload
        payload_parts = [method.upper(), url, str(timestamp)]
        
        # Add nonce if required
        if nonce:
            payload_parts.append(nonce)
            self._store_nonce(nonce, config.max_nonce_age_seconds)
        
        # Add body hash if required
        if config.include_body_hash and body:
            body_hash = hashlib.sha256(body).hexdigest()
            payload_parts.append(body_hash)
        
        # Add query parameters if required
        if config.include_query_params:
            parsed_url = urllib.parse.urlparse(url)
            if parsed_url.query:
                # Sort parameters for consistent signing
                params = urllib.parse.parse_qsl(parsed_url.query)
                sorted_params = sorted(params)
                payload_parts.append(urllib.parse.urlencode(sorted_params))
        
        # Add custom claims
        if custom_claims:
            claims_json = json.dumps(
                custom_claims, sort_keys=True, separators=(",", ":")
            )
            payload_parts.append(claims_json)
        
        # Create signature payload
        payload = "|".join(payload_parts)
        
        # Generate signature
        signature = self._generate_signature(payload, config)
        
        # Build signature headers
        signature_headers = {
            "X-Signature-Algorithm": config.algorithm.value,
            "X-Signature-KeyID": config.key_id,
            "X-Signature-Timestamp": str(timestamp),
            "X-Signature": signature,
        }
        
        if nonce:
            signature_headers["X-Signature-Nonce"] = nonce
        
        # Add child safety headers for child interactions
        if level == RequestSecurityLevel.CHILD_INTERACTION:
            signature_headers.update(
                {
                    "X-Child-Request": "true",
                    "X-COPPA-Protected": "true",
                    "X-Content-Safety": "required",
                }
            )
        
        logger.debug(
            f"Generated signature for {method} {url} with level {level.value}"
        )
        return signature_headers

    def validate_request_signature(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        body: Optional[bytes] = None,
        level: Optional[RequestSecurityLevel] = None,
    ) -> SignatureValidationResult:
        """
        Validate a signed HTTP request.
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            body: Request body bytes
            level: Expected security level
        Returns:
            SignatureValidationResult with validation details
        """
        level = level or self.default_level
        config = self.configurations[level]
        
        # Check for required signature headers
        required_headers = [
            "X-Signature",
            "X-Signature-Timestamp",
            "X-Signature-KeyID",
        ]
        missing_headers = [h for h in required_headers if h not in headers]
        if missing_headers:
            return SignatureValidationResult(
                valid=False,
                reason=f"Missing signature headers: {', '.join(missing_headers)}",
                security_flags=["missing_signature_headers"],
            )
        
        # Validate timestamp
        try:
            request_timestamp = int(headers["X-Signature-Timestamp"])
            current_time = int(time.time())
            time_diff = abs(current_time - request_timestamp)
            if time_diff > config.timestamp_tolerance_seconds:
                return SignatureValidationResult(
                    valid=False,
                    reason=(
                        f"Request timestamp outside tolerance "
                        f"({time_diff}s > {config.timestamp_tolerance_seconds}s)"
                    ),
                    timestamp=datetime.fromtimestamp(request_timestamp),
                    security_flags=["timestamp_out_of_tolerance"],
                )
        except (ValueError, KeyError):
            return SignatureValidationResult(
                valid=False,
                reason="Invalid timestamp format",
                security_flags=["invalid_timestamp"],
            )
        
        # Validate key ID
        if headers["X-Signature-KeyID"] != config.key_id:
            return SignatureValidationResult(
                valid=False,
                reason="Invalid key ID",
                key_id=headers.get("X-Signature-KeyID"),
                security_flags=["invalid_key_id"],
            )
        
        # Validate algorithm
        expected_algorithm = config.algorithm.value
        provided_algorithm = headers.get("X-Signature-Algorithm", "")
        if provided_algorithm != expected_algorithm:
            return SignatureValidationResult(
                valid=False,
                reason=(
                    f"Algorithm mismatch: expected {expected_algorithm}, "
                    f"got {provided_algorithm}"
                ),
                algorithm=provided_algorithm,
                security_flags=["algorithm_mismatch"],
            )
        
        # Validate nonce if required
        if config.require_nonce:
            nonce = headers.get("X-Signature-Nonce")
            if not nonce:
                return SignatureValidationResult(
                    valid=False,
                    reason="Missing required nonce",
                    security_flags=["missing_nonce"],
                )
            # Check nonce reuse
            if not self._validate_nonce(nonce, config.max_nonce_age_seconds):
                return SignatureValidationResult(
                    valid=False,
                    reason="Invalid or reused nonce",
                    security_flags=["invalid_nonce"],
                )
        
        # Rebuild signature payload
        payload_parts = [method.upper(), url, str(request_timestamp)]
        
        # Add nonce if present
        if config.require_nonce and "X-Signature-Nonce" in headers:
            payload_parts.append(headers["X-Signature-Nonce"])
        
        # Add body hash if required
        if config.include_body_hash and body:
            body_hash = hashlib.sha256(body).hexdigest()
            payload_parts.append(body_hash)
        
        # Add query parameters if required
        if config.include_query_params:
            parsed_url = urllib.parse.urlparse(url)
            if parsed_url.query:
                params = urllib.parse.parse_qsl(parsed_url.query)
                sorted_params = sorted(params)
                payload_parts.append(urllib.parse.urlencode(sorted_params))
        
        # Create expected payload
        payload = "|".join(payload_parts)
        
        # Generate expected signature
        expected_signature = self._generate_signature(payload, config)
        provided_signature = headers["X-Signature"]
        
        # Constant-time comparison to prevent timing attacks
        if not hmac.compare_digest(expected_signature, provided_signature):
            return SignatureValidationResult(
                valid=False,
                reason="Signature verification failed",
                timestamp=datetime.fromtimestamp(request_timestamp),
                key_id=headers["X-Signature-KeyID"],
                algorithm=provided_algorithm,
                security_flags=["signature_mismatch"],
            )
        
        # Check for replay attacks
        signature_hash = hashlib.sha256(
            provided_signature.encode()
        ).hexdigest()
        if signature_hash in self.signature_cache:
            return SignatureValidationResult(
                valid=False,
                reason="Potential replay attack detected",
                timestamp=datetime.fromtimestamp(request_timestamp),
                security_flags=["replay_attack"],
            )
        
        # Store signature to prevent replay
        self.signature_cache[signature_hash] = datetime.utcnow()
        
        # Cleanup caches periodically
        self._cleanup_caches()
        
        logger.debug(f"Successfully validated signature for {method} {url}")
        return SignatureValidationResult(
            valid=True,
            timestamp=datetime.fromtimestamp(request_timestamp),
            key_id=headers["X-Signature-KeyID"],
            algorithm=provided_algorithm,
        )

    def _generate_signature(
        self, payload: str, config: SignatureConfiguration
    ) -> str:
        """Generate HMAC signature for payload."""
        if config.algorithm == SignatureAlgorithm.HMAC_SHA256:
            digest = hmac.new(
                config.secret_key, payload.encode("utf-8"), hashlib.sha256
            )
        elif config.algorithm == SignatureAlgorithm.HMAC_SHA512:
            digest = hmac.new(
                config.secret_key, payload.encode("utf-8"), hashlib.sha512
            )
        else:
            raise ValueError(f"Unsupported algorithm: {config.algorithm}")
        return base64.b64encode(digest.digest()).decode("ascii")

    def _generate_nonce(self) -> str:
        """Generate cryptographically secure nonce."""
        return base64.b64encode(secrets.token_bytes(16)).decode("ascii")

    def _store_nonce(self, nonce: str, max_age_seconds: int) -> None:
        """Store nonce with expiration."""
        self.nonce_cache[nonce] = datetime.utcnow()
        # Clean up expired nonces
        if len(self.nonce_cache) > self.max_cache_size:
            self._cleanup_nonce_cache(max_age_seconds)

    def _validate_nonce(self, nonce: str, max_age_seconds: int) -> bool:
        """Validate nonce is new and within time window."""
        if nonce in self.nonce_cache:
            # Nonce already used - potential replay attack
            logger.warning(f"Nonce reuse detected: {nonce}")
            return False
        # Store nonce to prevent reuse
        self.nonce_cache[nonce] = datetime.utcnow()
        return True

    def _cleanup_nonce_cache(self, max_age_seconds: int) -> None:
        """Remove expired nonces from cache."""
        cutoff = datetime.utcnow() - timedelta(seconds=max_age_seconds)
        expired_nonces = [
            nonce
            for nonce, created in self.nonce_cache.items()
            if created < cutoff
        ]
        for nonce in expired_nonces:
            del self.nonce_cache[nonce]
        logger.debug(f"Cleaned up {len(expired_nonces)} expired nonces")

    def _cleanup_caches(self) -> None:
        """Cleanup all caches periodically."""
        now = datetime.utcnow()
        if now - self.last_cleanup < self.cache_cleanup_interval:
            return
        
        # Clean signature cache (prevent replay attacks)
        signature_cutoff = now - timedelta(
            hours=24
        )  # Keep signatures for 24 hours
        expired_signatures = [
            sig
            for sig, created in self.signature_cache.items()
            if created < signature_cutoff
        ]
        for sig in expired_signatures:
            del self.signature_cache[sig]
        
        # Clean nonce cache for all configurations
        for config in self.configurations.values():
            self._cleanup_nonce_cache(config.max_nonce_age_seconds)
        
        self.last_cleanup = now
        logger.debug("Completed cache cleanup")

    def get_signing_statistics(self) -> Dict[str, Any]:
        """Get signing service statistics for monitoring."""
        return {
            "default_level": self.default_level.value,
            "active_nonces": len(self.nonce_cache),
            "cached_signatures": len(self.signature_cache),
            "configurations": {
                level.value: {
                    "algorithm": config.algorithm.value,
                    "key_id": config.key_id,
                    "timestamp_tolerance": config.timestamp_tolerance_seconds,
                    "requires_nonce": config.require_nonce,
                }
                for level, config in self.configurations.items()
            },
            "last_cleanup": self.last_cleanup.isoformat(),
        }

    def rotate_signing_key(
        self, level: RequestSecurityLevel, new_secret_key: bytes
    ) -> bool:
        """
        Rotate signing key for a security level.
        Args:
            level: Security level to update
            new_secret_key: New secret key
        Returns:
            True if successful
        """
        try:
            config = self.configurations[level]
            old_key_id = config.key_id
            # Generate new key ID
            new_key_id = f"{level.value}_v{int(time.time())}"
            # Update configuration
            config.secret_key = new_secret_key
            config.key_id = new_key_id
            # Clear related caches
            self.nonce_cache.clear()
            self.signature_cache.clear()
            logger.info(
                f"Rotated signing key for {level.value}: {old_key_id} -> {new_key_id}"
            )
            return True
        except Exception as e:
            logger.error(
                f"Failed to rotate signing key for {level.value}: {e}"
            )
            return False

    def create_child_safe_headers(
        self, child_id: str, age: int
    ) -> Dict[str, str]:
        """
        Create additional headers for child safety.
        Args:
            child_id: Child identifier
            age: Child's age
        Returns:
            Dict of child safety headers
        """
        headers = {
            "X-Child-ID": child_id,
            "X-Child-Age-Group": self._get_age_group(age),
            "X-COPPA-Subject": "true" if age < 13 else "false",
            "X-Content-Filter": "strict",
            "X-Parental-Controls": "active",
        }
        return headers

    def _get_age_group(self, age: int) -> str:
        """Get age group for child safety headers."""
        if age <= 4:
            return "toddler"
        elif age <= 7:
            return "preschool"
        elif age <= 12:
            return "school-age"
        else:
            return "teen"