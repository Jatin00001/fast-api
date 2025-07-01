# schemas/image.py
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Optional, List


class ImageBase(BaseModel):
    """Base image schema with common attributes"""
    filename: Optional[str] = Field(None, max_length=255, description="Original filename")
    image_url: Optional[str] = Field(None, description="Primary image URL")
    backup_image_url: Optional[str] = Field(None, description="Backup image URL")
    description: Optional[str] = Field(None, max_length=1000, description="Image description")
    alt_text: Optional[str] = Field(None, max_length=255, description="Alt text for accessibility")
    order: Optional[int] = Field(default=0, ge=0, le=9999, description="Display order")
    is_active: bool = Field(default=True, description="Whether image is active")
    is_deleted: bool = Field(default=False, description="Soft delete flag")


class ImageCreate(BaseModel):
    """Schema for creating a new image"""
    filename: str = Field(..., min_length=1, max_length=255, description="Original filename")
    image_url: str = Field(..., description="Primary image URL")
    backup_image_url: Optional[str] = Field(None, description="Backup image URL")
    description: Optional[str] = Field(None, max_length=1000, description="Image description")
    alt_text: Optional[str] = Field(None, max_length=255, description="Alt text for accessibility")
    order: int = Field(default=0, ge=0, le=9999, description="Display order")
    file_id: Optional[int] = Field(None, description="Associated file ID")

    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v):
        """Normalize filename to lowercase for consistency"""
        if v:
            # Convert to lowercase and normalize
            v = v.lower().strip()
            # Replace spaces with hyphens for URL-friendliness
            import re
            v = re.sub(r'\s+', '-', v)
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "sample-image.jpg",
                "image_url": "https://example.com/images/sample-image.jpg",
                "backup_image_url": "https://backup.example.com/images/sample-image.jpg",
                "description": "A beautiful sample image",
                "alt_text": "Sample image showing beautiful scenery",
                "order": 1,
                "file_id": 123
            }
        }
    )


class ImageUpdate(BaseModel):
    """Schema for updating an image"""
    filename: Optional[str] = Field(None, min_length=1, max_length=255, description="Original filename")
    image_url: Optional[str] = Field(None, description="Primary image URL")
    backup_image_url: Optional[str] = Field(None, description="Backup image URL")
    description: Optional[str] = Field(None, max_length=1000, description="Image description")
    alt_text: Optional[str] = Field(None, max_length=255, description="Alt text for accessibility")
    order: Optional[int] = Field(None, ge=0, le=9999, description="Display order")
    is_active: Optional[bool] = Field(None, description="Whether image is active")
    is_deleted: Optional[bool] = Field(None, description="Soft delete flag")

    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v):
        """Normalize filename to lowercase for consistency"""
        if v:
            # Convert to lowercase and normalize
            v = v.lower().strip()
            # Replace spaces with hyphens for URL-friendliness
            import re
            v = re.sub(r'\s+', '-', v)
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "description": "Updated image description",
                "alt_text": "Updated alt text",
                "order": 2,
                "is_active": True
            }
        }
    )


class ImageOut(ImageBase):
    """Schema for image responses"""
    id: int = Field(..., description="Image ID")
    file_id: Optional[int] = Field(None, description="Associated file ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "filename": "sample-image.jpg",
                "image_url": "https://example.com/images/sample-image.jpg",
                "backup_image_url": "https://backup.example.com/images/sample-image.jpg",
                "description": "A beautiful sample image",
                "alt_text": "Sample image showing beautiful scenery",
                "order": 1,
                "is_active": True,
                "is_deleted": False,
                "file_id": 123,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T12:00:00Z"
            }
        }
    )


class ImageResponse(ImageOut):
    """Alias for ImageOut for backward compatibility"""
    pass


class ImageListResponse(BaseModel):
    """Schema for image list responses"""
    images: List[ImageOut] = Field(..., description="List of images")
    total: int = Field(..., description="Total number of images")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "images": [],
                "total": 0,
                "page": 1,
                "limit": 100
            }
        }
    )


class ImageUploadResponse(BaseModel):
    """Schema for image upload responses"""
    image: ImageOut = Field(..., description="Uploaded image data")
    message: str = Field(..., description="Success message")
    upload_time: datetime = Field(default_factory=lambda: datetime.utcnow(), description="Upload timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "image": {
                    "id": 1,
                    "filename": "uploaded-image.jpg",
                    "image_url": "https://example.com/images/uploaded-image.jpg",
                    "is_active": True
                },
                "message": "Image uploaded successfully",
                "upload_time": "2025-01-01T12:00:00Z"
            }
        }
    )
