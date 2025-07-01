from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


class FileBase(BaseModel):
    """Base file schema with common attributes"""
    identifier: Optional[str] = Field(None, max_length=255, description="Unique file identifier")
    filename: Optional[str] = Field(None, max_length=255, description="Original filename")
    content_type: Optional[str] = Field(None, max_length=100, description="MIME content type")
    size: Optional[int] = Field(None, ge=0, description="File size in bytes")
    message: Optional[str] = Field(None, max_length=1000, description="File description or message")
    is_deleted: bool = Field(default=False, description="Soft delete flag")


class FileCreate(BaseModel):
    """Schema for creating a new file"""
    identifier: str = Field(..., min_length=1, max_length=255, description="Unique file identifier")
    filename: str = Field(..., min_length=1, max_length=255, description="Original filename")
    content_type: str = Field(..., min_length=1, max_length=100, description="MIME content type")
    size: int = Field(..., ge=0, description="File size in bytes")
    message: Optional[str] = Field(None, max_length=1000, description="File description or message")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "identifier": "file_12345",
                "filename": "document.pdf",
                "content_type": "application/pdf",
                "size": 1024000,
                "message": "Important document upload"
            }
        }
    )


class FileUpdate(BaseModel):
    """Schema for updating a file"""
    identifier: Optional[str] = Field(None, min_length=1, max_length=255, description="Unique file identifier")
    filename: Optional[str] = Field(None, min_length=1, max_length=255, description="Original filename")
    content_type: Optional[str] = Field(None, min_length=1, max_length=100, description="MIME content type")
    size: Optional[int] = Field(None, ge=0, description="File size in bytes")
    message: Optional[str] = Field(None, max_length=1000, description="File description or message")
    is_deleted: Optional[bool] = Field(None, description="Soft delete flag")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "updated_document.pdf",
                "message": "Updated document description",
                "is_deleted": False
            }
        }
    )


class FileOut(FileBase):
    """Schema for file responses"""
    id: int = Field(..., description="File ID")
    public_url: Optional[str] = Field(None, description="Public URL for file access")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "identifier": "file_12345",
                "filename": "document.pdf",
                "content_type": "application/pdf",
                "size": 1024000,
                "message": "Important document upload",
                "is_deleted": False,
                "public_url": "https://example.com/files/document.pdf",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T12:00:00Z"
            }
        }
    )


# Alias for backward compatibility
FileRead = FileOut
FileResponse = FileOut


class FileListResponse(BaseModel):
    """Schema for file list responses"""
    files: List[FileOut] = Field(..., description="List of files")
    total: int = Field(..., description="Total number of files")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "files": [],
                "total": 0,
                "page": 1,
                "limit": 100
            }
        }
    )


class FileUploadResponse(BaseModel):
    """Schema for file upload responses"""
    file: FileOut = Field(..., description="Uploaded file data")
    message: str = Field(..., description="Success message")
    upload_time: datetime = Field(default_factory=lambda: datetime.utcnow(), description="Upload timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file": {
                    "id": 1,
                    "filename": "uploaded_file.pdf",
                    "content_type": "application/pdf",
                    "size": 1024000,
                    "public_url": "https://example.com/files/uploaded_file.pdf"
                },
                "message": "File uploaded successfully",
                "upload_time": "2025-01-01T12:00:00Z"
            }
        }
    )