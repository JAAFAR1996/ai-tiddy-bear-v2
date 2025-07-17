from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
from jose import jwt, JWTError
from src.infrastructure.config.settings import get_settings
from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="security")

from src.infrastructure.config.settings import Settings, get_settings
from fastapi import Depends

class TokenService:
    """Service for creating, verifying, and managing JWT tokens."""
    def __init__(self, settings: Settings=Depends(get_settings)) -> None:
        self.settings = settings
        self.secret_key = self.settings.security.SECRET_KEY
        self.algorithm = self.settings.security.JWT_ALGORITHM
        self.access_token_expire_minutes = (self.settings.security.ACCESS_TOKEN_EXPIRE_MINUTES)
        self.refresh_token_expire_days = (self.settings.security.REFRESH_TOKEN_EXPIRE_DAYS)
        
        if not self.secret_key or len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT access token with user data."""
        try:
            to_encode = {
                "sub": user_data["id"],
                "email": user_data["email"],
                "role": user_data["role"],
                "type": "access",
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes),
            }
            return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        except (KeyError, TypeError) as e:
            logger.error(f"Invalid user data for token creation: {e}")
            raise ValueError("Failed to create access token")
        except JWTError as e:
            logger.error(f"JWT encoding error: {e}")
            raise ValueError("Failed to create access token")
    
    def create_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT refresh token."""
        try:
            to_encode = {
                "sub": user_data["id"],
                "email": user_data["email"],
                "type": "refresh",
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
            }
            return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        except (KeyError, TypeError) as e:
            logger.error(f"Invalid user data for refresh token: {e}")
            raise ValueError("Failed to create refresh token")
        except JWTError as e:
            logger.error(f"JWT encoding error for refresh token: {e}")
            raise ValueError("Failed to create refresh token")
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and check blacklist (if Redis cache is provided)."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            # Blacklist check would typically be done by the calling service (e.g., AuthService)
            return payload
        except jwt.ExpiredSignatureError:
            logger.debug("Token has expired")
            return None
        except JWTError as e:
            logger.debug(f"Token validation failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None