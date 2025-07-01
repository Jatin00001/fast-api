from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List
from datetime import datetime

class CityBase(BaseModel):
    """Base city schema with common attributes"""
    name: str = Field(..., min_length=1, max_length=100, description="City name")
    slug: str = Field(..., min_length=1, max_length=100, description="URL-friendly city identifier")
    is_active: bool = Field(default=True, description="Whether city is active")
    country_id: Optional[int] = Field(None, description="Associated country ID")
    image_id: Optional[int] = Field(None, description="Associated image ID")
    image_url: Optional[str] = Field(None, description="City image URL")
    order: int = Field(default=9999, ge=0, le=9999, description="Display order")

class CityCreate(CityBase):
    """Schema for creating a new city"""
    name: str = Field(..., min_length=1, max_length=100, description="City name")
    slug: str = Field(..., min_length=1, max_length=100, description="URL-friendly city identifier")
    country_id: int = Field(..., description="Associated country ID")

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        """Ensure slug is lowercase and URL-friendly"""
        if v:
            # Convert to lowercase and replace spaces with hyphens
            v = v.lower().strip()
            # Replace multiple spaces/hyphens with single hyphen
            import re
            v = re.sub(r'[\s_]+', '-', v)
            v = re.sub(r'-+', '-', v)
            # Remove leading/trailing hyphens
            v = v.strip('-')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "New York",
                "slug": "new-york",
                "is_active": True,
                "country_id": 1,
                "image_url": "https://example.com/images/new-york.jpg",
                "order": 1
            }
        }
    )

class CityUpdate(BaseModel):
    """Schema for updating a city"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="City name")
    slug: Optional[str] = Field(None, min_length=1, max_length=100, description="URL-friendly city identifier")
    is_active: Optional[bool] = Field(None, description="Whether city is active")
    country_id: Optional[int] = Field(None, description="Associated country ID")
    image_id: Optional[int] = Field(None, description="Associated image ID")
    image_url: Optional[str] = Field(None, description="City image URL")
    order: Optional[int] = Field(None, ge=0, le=9999, description="Display order")

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        """Ensure slug is lowercase and URL-friendly"""
        if v:
            # Convert to lowercase and replace spaces with hyphens
            v = v.lower().strip()
            # Replace multiple spaces/hyphens with single hyphen
            import re
            v = re.sub(r'[\s_]+', '-', v)
            v = re.sub(r'-+', '-', v)
            # Remove leading/trailing hyphens
            v = v.strip('-')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated City Name",
                "is_active": True,
                "order": 2
            }
        }
    )

class CityOut(CityBase):
    """Schema for city responses"""
    id: int = Field(..., description="City ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "New York",
                "slug": "new-york",
                "is_active": True,
                "country_id": 1,
                "image_id": 10,
                "image_url": "https://example.com/images/new-york.jpg",
                "order": 1,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T12:00:00Z"
            }
        }
    )

# Alias for backward compatibility
CityResponse = CityOut

class CityWithCountry(CityOut):
    """Schema for city with country information"""
    country_name: Optional[str] = Field(None, description="Country name")
    country_code: Optional[str] = Field(None, description="Country code")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "New York",
                "slug": "new-york",
                "country_name": "United States",
                "country_code": "US",
                "is_active": True
            }
        }
    )

class CityListResponse(BaseModel):
    """Schema for city list responses"""
    cities: List[CityOut] = Field(..., description="List of cities")
    total: int = Field(..., description="Total number of cities")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cities": [],
                "total": 0,
                "page": 1,
                "limit": 100
            }
        }
    )

class CitySearchResponse(BaseModel):
    """Schema for city search responses"""
    cities: List[CityOut] = Field(..., description="List of matching cities")
    search_term: str = Field(..., description="Search term used")
    total_results: int = Field(..., description="Total number of results")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cities": [],
                "search_term": "New",
                "total_results": 0
            }
        }
    )
