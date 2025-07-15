"""
Authentication Endpoints Generator for AI Teddy Bear API
"""

import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class AuthEndpointsGenerator:
    """مولد endpoints المصادقة"""
    
    def __init__(self, base_path: str = "src/presentation/api/endpoints"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def generate_auth_endpoints(self) -> None:
        """إنشاء endpoints المصادقة"""
        
        logger.info("🔐 Creating authentication endpoints...")
        
        auth_endpoints_content = '''"""
API endpoints للمصادقة والتفويض
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

try:
    from fastapi import APIRouter, HTTPException, Depends, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from pydantic import BaseModel, EmailStr
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    
    # Mock classes for development
    class APIRouter:
        def __init__(self, *args, **kwargs):
            self.routes = []
        def post(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        def get(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    
    class BaseModel:
        pass
    
    class HTTPException(Exception):
        def __init__(self, status_code, detail):
            self.status_code = status_code
            self.detail = detail

logger = logging.getLogger(__name__)

# Pydantic models
class LoginRequest(BaseModel):
    """نموذج طلب تسجيل الدخول"""
    email: str
    password: str

class RegisterRequest(BaseModel):
    """نموذج طلب التسجيل"""
    email: str
    password: str
    parent_name: str
    child_name: str
    child_age: int

class TokenResponse(BaseModel):
    """نموذج استجابة التوكن"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserProfile(BaseModel):
    """نموذج ملف المستخدم"""
    id: str
    email: str
    parent_name: str
    child_name: str
    child_age: int
    is_active: bool
    created_at: datetime

# Create router
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

# Security scheme
security = HTTPBearer() if FASTAPI_AVAILABLE else None

@auth_router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest) -> TokenResponse:
    """تسجيل دخول المستخدم"""
    
    try:
        # Import auth service
        from ....infrastructure.security.real_auth_service import auth_service
        
        # Authenticate user
        user = auth_service.authenticate_user(login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create tokens
        token_data = {"sub": user["id"], "email": user["email"], "role": user["role"]}
        access_token = auth_service.create_access_token(token_data)
        refresh_token = auth_service.create_refresh_token(token_data)
        
        logger.info(f"User logged in successfully: {user['email']}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800  # 30 minutes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@auth_router.post("/register", response_model=UserProfile)
async def register(register_data: RegisterRequest) -> UserProfile:
    """تسجيل مستخدم جديد"""
    
    try:
        # Validate child age for COPPA compliance
        if register_data.child_age > 13:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Child age must be 13 or under for COPPA compliance"
            )
        
        # TODO #021: Implement user registration logic
        # This would typically involve:
        # 1. Check if email already exists
        # 2. Hash the password
        # 3. Create user in database
        # 4. Send verification email
        
        logger.info(f"New user registration: {register_data.email}")
        
        # Mock response for now
        return UserProfile(
            id="new-user-id",
            email=register_data.email,
            parent_name=register_data.parent_name,
            child_name=register_data.child_name,
            child_age=register_data.child_age,
            is_active=True,
            created_at=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@auth_router.get("/profile", response_model=UserProfile)
async def get_profile(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserProfile:
    """الحصول على ملف المستخدم"""
    
    try:
        from ....infrastructure.security.real_auth_service import auth_service
        
        # Verify token
        payload = auth_service.verify_token(credentials.credentials)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # TODO #022: Get user from database
        # Mock response for now
        return UserProfile(
            id=payload["sub"],
            email=payload["email"],
            parent_name="Demo Parent",
            child_name="Demo Child",
            child_age=6,
            is_active=True,
            created_at=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )

@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenResponse:
    """تجديد التوكن"""
    
    try:
        from ....infrastructure.security.real_auth_service import auth_service
        
        # Verify refresh token
        payload = auth_service.verify_token(credentials.credentials)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new access token
        token_data = {"sub": payload["sub"], "email": payload["email"], "role": payload.get("role", "parent")}
        new_access_token = auth_service.create_access_token(token_data)
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=credentials.credentials,  # Keep same refresh token
            expires_in=1800
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )

@auth_router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, str]:
    """تسجيل خروج المستخدم"""
    
    try:
        # TODO #023: Implement token blacklist
        # For now, just return success
        logger.info("User logged out successfully")
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

# Export router
__all__ = ["auth_router"]
'''
        
        # Write the file
        auth_file = self.base_path / "auth.py"
        with open(auth_file, 'w', encoding='utf-8') as f:
            f.write(auth_endpoints_content)
        
        logger.info("✅ Authentication endpoints created successfully")
    
    def generate_auth_schemas(self) -> None:
        """إنشاء schemas المصادقة"""
        
        schemas_path = Path("src/presentation/api/schemas")
        schemas_path.mkdir(parents=True, exist_ok=True)
        
        schemas_content = '''"""
Authentication Schemas for AI Teddy Bear API
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class LoginSchema(BaseModel):
    """مخطط تسجيل الدخول"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")

class RegisterSchema(BaseModel):
    """مخطط التسجيل"""
    email: EmailStr = Field(..., description="Parent email address")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    parent_name: str = Field(..., min_length=2, max_length=100, description="Parent full name")
    child_name: str = Field(..., min_length=2, max_length=50, description="Child name")
    child_age: int = Field(..., ge=3, le=13, description="Child age (3-13 for COPPA compliance)")

class TokenSchema(BaseModel):
    """مخطط التوكن"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserProfileSchema(BaseModel):
    """مخطط ملف المستخدم"""
    id: str
    email: EmailStr
    parent_name: str
    child_name: str
    child_age: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

class PasswordChangeSchema(BaseModel):
    """مخطط تغيير كلمة المرور"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")
    confirm_password: str = Field(..., description="Confirm new password")

class PasswordResetRequestSchema(BaseModel):
    """مخطط طلب إعادة تعيين كلمة المرور"""
    email: EmailStr = Field(..., description="Email address for password reset")

class PasswordResetSchema(BaseModel):
    """مخطط إعادة تعيين كلمة المرور"""
    reset_token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")
'''
        
        schemas_file = schemas_path / "auth_schemas.py"
        with open(schemas_file, 'w', encoding='utf-8') as f:
            f.write(schemas_content)
        
        logger.info("✅ Authentication schemas created successfully")