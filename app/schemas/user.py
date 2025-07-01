from datetime import datetime
from typing import Annotated, Optional, List

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from pydantic.types import constr

class UserBase(BaseModel):
    """Base user schema with common attributes"""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    is_active: bool = Field(default=True, description="Whether user is active")
    is_superuser: bool = Field(default=False, description="Whether user has admin privileges")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validate username format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v.lower()

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format"""
        return v.lower()

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, max_length=100, description="User password")
    password_confirm: str = Field(..., description="Password confirmation")

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v):
        """Validate password complexity"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v

    @field_validator('password_confirm')
    @classmethod
    def passwords_match(cls, v, info):
        """Validate that passwords match"""
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "username": "john_doe",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "is_active": True,
                "is_superuser": False
            }
        }
    )

class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = Field(None, description="User email address")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    password: Optional[str] = Field(None, min_length=8, max_length=100, description="New password")
    is_active: Optional[bool] = Field(None, description="Whether user is active")
    is_superuser: Optional[bool] = Field(None, description="Whether user has admin privileges")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validate username format"""
        if v is not None and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v.lower() if v else v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format"""
        return v.lower() if v else v

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v):
        """Validate password complexity"""
        if v is not None:
            if not any(c.isupper() for c in v):
                raise ValueError('Password must contain at least one uppercase letter')
            if not any(c.islower() for c in v):
                raise ValueError('Password must contain at least one lowercase letter')
            if not any(c.isdigit() for c in v):
                raise ValueError('Password must contain at least one number')
            if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
                raise ValueError('Password must contain at least one special character')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "updated@example.com",
                "username": "updated_username",
                "password": "NewSecurePass123!",
                "is_active": True
            }
        }
    )

class UserOut(UserBase):
    """Schema for user responses"""
    id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "john_doe",
                "is_active": True,
                "is_superuser": False,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T12:00:00Z"
            }
        }
    )

# Aliases for backward compatibility
User = UserOut
UserResponse = UserOut

class UserInDB(UserBase):
    """Internal user schema with database fields"""
    id: int = Field(..., description="User ID")
    hashed_password: str = Field(..., description="Hashed password")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)

class UserListResponse(BaseModel):
    """Schema for user list responses"""
    users: List[UserOut] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "users": [],
                "total": 0,
                "page": 1,
                "limit": 100
            }
        }
    )

class Token(BaseModel):
    """Schema for token (backward compatibility)"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )

class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", pattern="^bearer$", description="Token type")
    expires_in: Optional[int] = Field(None, description="Token expiration time in seconds")
    user: Optional[UserOut] = Field(None, description="User information")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "username": "john_doe"
                }
            }
        }
    )

class TokenPayload(BaseModel):
    """Schema for token payload"""
    sub: str = Field(..., description="Subject (user ID)")
    exp: datetime = Field(..., description="Expiration time")
    iat: Optional[datetime] = Field(None, description="Issued at time")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sub": "123",
                "exp": "2024-12-31T23:59:59Z",
                "iat": "2024-01-01T00:00:00Z"
            }
        }
    )

class UserProfile(UserOut):
    """Extended user profile schema"""
    login_count: Optional[int] = Field(default=0, description="Number of logins")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "john_doe",
                "is_active": True,
                "is_superuser": False,
                "login_count": 25,
                "last_login": "2025-01-01T10:30:00Z",
                "created_at": "2025-01-01T00:00:00Z"
            }
        }
    )