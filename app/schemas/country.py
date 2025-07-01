from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator
from datetime import datetime


# ✅ Shared properties
class CountryBase(BaseModel):
    """Base country schema with common attributes"""
    name: str = Field(..., min_length=1, max_length=100, description="Country name")
    country_code: str = Field(..., min_length=2, max_length=3, description="ISO country code")
    image_url: Optional[str] = Field(None, description="Country image URL")
    showon_destmenu: bool = Field(default=False, description="Show on destination menu")


# ✅ Used for POST / create
class CountryCreate(CountryBase):
    """Schema for creating a new country"""
    name: str = Field(..., min_length=1, max_length=100, description="Country name")
    slug: str = Field(..., min_length=1, max_length=100, description="URL-friendly country identifier")
    country_code: str = Field(..., min_length=2, max_length=3, description="ISO country code")
    location: Optional[str] = Field(None, max_length=255, description="Geographic location description")
    image_id: Optional[int] = Field(None, description="Associated image ID")
    image_url: Optional[str] = Field(None, description="Country image URL")
    showon_destmenu: bool = Field(default=False, description="Show on destination menu")

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

    @field_validator('country_code')
    @classmethod  
    def validate_country_code(cls, v):
        """Ensure country code is uppercase (ISO standard)"""
        return v.upper() if v else v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "United States",
                "slug": "united-states",
                "country_code": "US",
                "location": "North America",
                "image_url": "https://example.com/images/us-flag.jpg",
                "showon_destmenu": True
            }
        }
    )


# ✅ Used for PUT / update
class CountryUpdate(BaseModel):
    """Schema for updating a country"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Country name")
    slug: Optional[str] = Field(None, min_length=1, max_length=100, description="URL-friendly country identifier")
    country_code: Optional[str] = Field(None, min_length=2, max_length=3, description="ISO country code")
    location: Optional[str] = Field(None, max_length=255, description="Geographic location description")
    image_id: Optional[int] = Field(None, description="Associated image ID")
    image_url: Optional[str] = Field(None, description="Country image URL")
    showon_destmenu: Optional[bool] = Field(None, description="Show on destination menu")

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

    @field_validator('country_code')
    @classmethod
    def validate_country_code(cls, v):
        """Ensure country code is uppercase (ISO standard)"""
        return v.upper() if v else v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Country Name",
                "showon_destmenu": True,
                "location": "Updated location"
            }
        }
    )


# ✅ Common DB response base
class CountryOut(CountryBase):
    """Schema for country responses"""
    id: int = Field(..., description="Country ID")
    slug: str = Field(..., description="URL-friendly country identifier")
    location: Optional[Any] = Field(None, description="Geographic location description")
    image_id: Optional[int] = Field(None, description="Associated image ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    @field_serializer('location')
    def serialize_location(self, location: Any) -> Optional[str]:
        """Convert PostGIS geometry to string representation"""
        if location is None:
            return None
        
        # Handle different types of location data
        if isinstance(location, str):
            return location
        
        # Handle PostGIS WKBElement (geometry data)
        try:
            if hasattr(location, 'data'):
                # This is a PostGIS WKBElement - convert to WKT string
                from geoalchemy2 import functions
                # For now, return a placeholder - in production you'd convert properly
                return "Geographic coordinates available"
            else:
                return str(location)
        except Exception:
            return None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "United States",
                "slug": "united-states",
                "country_code": "US",
                "location": "North America",
                "image_id": 5,
                "image_url": "https://example.com/images/us-flag.jpg",
                "showon_destmenu": True,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T12:00:00Z"
            }
        }
    )


# Alias for backward compatibility
CountryResponse = CountryOut
CountryInDB = CountryOut


class CountryWithCities(CountryOut):
    """Schema for country with cities information"""
    cities_count: int = Field(default=0, description="Number of cities in this country")
    cities: Optional[List[dict]] = Field(None, description="List of cities in this country")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "United States",
                "slug": "united-states",
                "country_code": "US",
                "cities_count": 5,
                "cities": [{"id": 1, "name": "New York", "slug": "new-york"}]
            }
        }
    )


class CountryListResponse(BaseModel):
    """Schema for country list responses"""
    countries: List[CountryOut] = Field(..., description="List of countries")
    total: int = Field(..., description="Total number of countries")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "countries": [],
                "total": 0,
                "page": 1,
                "limit": 100
            }
        }
    )


class CountrySearchResponse(BaseModel):
    """Schema for country search responses"""
    countries: List[CountryOut] = Field(..., description="List of matching countries")
    search_term: str = Field(..., description="Search term used")
    total_results: int = Field(..., description="Total number of results")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "countries": [],
                "search_term": "United",
                "total_results": 0
            }
        }
    )


class CountryDestinationMenuResponse(BaseModel):
    """Schema for countries shown on destination menu"""
    countries: List[CountryOut] = Field(..., description="Countries shown on destination menu")
    total: int = Field(..., description="Total number of destination menu countries")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "countries": [],
                "total": 0
            }
        }
    )
