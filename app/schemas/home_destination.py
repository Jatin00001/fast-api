from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional, List

class HomeDestinationBase(BaseModel):
    """Base schema for home destinations"""
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    order: int = Field(..., ge=1, le=999, description="Display order (1-999)")
    is_active: bool = Field(default=False, description="Whether destination is active")

class HomeDestinationCreate(HomeDestinationBase):
    """Schema for creating a home destination"""
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    order: int = Field(..., ge=1, le=999, description="Display order (1-999)")
    image_url: Optional[str] = Field(None, description="Destination image URL")

    @field_validator('city')
    @classmethod
    def validate_city(cls, v):
        """Normalize city name to lowercase for consistency in searching"""
        if v:
            # Convert to lowercase and normalize for search consistency
            v = v.lower().strip()
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "city": "Paris",
                "order": 1,
                "is_active": True,
                "image_url": "https://example.com/images/paris.jpg"
            }
        }
    )

class HomeDestinationUpdate(BaseModel):
    """Schema for updating a home destination"""
    city: Optional[str] = Field(None, min_length=1, max_length=100, description="City name")
    order: Optional[int] = Field(None, ge=1, le=999, description="Display order (1-999)")
    is_active: Optional[bool] = Field(None, description="Whether destination is active")
    image_url: Optional[str] = Field(None, description="Destination image URL")

    @field_validator('city')
    @classmethod
    def validate_city(cls, v):
        """Normalize city name to lowercase for consistency in searching"""
        if v:
            # Convert to lowercase and normalize for search consistency
            v = v.lower().strip()
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "city": "Updated Paris",
                "order": 2,
                "is_active": True
            }
        }
    )

class HomeDestinationOut(BaseModel):
    """Schema for home destination output"""
    id: int = Field(..., description="Destination ID")
    city: str = Field(..., description="City name")
    order: int = Field(..., description="Display order")
    is_active: bool = Field(..., description="Whether destination is active")
    image_url: Optional[str] = Field(None, description="Destination image URL")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "city": "Paris",
                "order": 1,
                "is_active": True,
                "image_url": "https://example.com/images/paris.jpg",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T12:00:00Z"
            }
        }
    )

# Legacy schema for backward compatibility
class HomePageDestinationOut(HomeDestinationOut):
    """Legacy schema name for backward compatibility"""
    pass

class HomeDestinationListResponse(BaseModel):
    """Schema for home destination list responses"""
    destinations: List[HomeDestinationOut] = Field(..., description="List of home destinations")
    total: int = Field(..., description="Total number of destinations")
    active_count: int = Field(..., description="Number of active destinations")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "destinations": [],
                "total": 0,
                "active_count": 0
            }
        }
    )

class ActiveHomeDestinationResponse(BaseModel):
    """Schema for active home destinations response"""
    destinations: List[HomeDestinationOut] = Field(..., description="List of active destinations")
    total: int = Field(..., description="Total number of active destinations")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "destinations": [],
                "total": 0
            }
        }
    )
