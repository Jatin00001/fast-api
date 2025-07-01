from pydantic import BaseModel, Field
from typing import Any, Optional, List, Union
from datetime import datetime

class BaseResponse(BaseModel):
    """Base response model for all API endpoints"""
    status: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow(), description="Response timestamp")

class SuccessResponse(BaseResponse):
    """Success response model with data"""
    data: Optional[Any] = Field(None, description="Response data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": 200,
                "message": "Success",
                "data": {},
                "timestamp": "2025-06-30T12:00:00Z"
            }
        }

class ErrorResponse(BaseResponse):
    """Error response model"""
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[dict] = Field(None, description="Error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": 400,
                "message": "Bad Request",
                "error_code": "VALIDATION_ERROR",
                "details": {"field": "error description"},
                "timestamp": "2025-06-30T12:00:00Z"
            }
        }

class ListResponse(BaseResponse):
    """List response model with pagination"""
    data: List[Any] = Field(default_factory=list, description="List of items")
    total: int = Field(0, description="Total number of items")
    page: int = Field(1, description="Current page number")
    limit: int = Field(100, description="Items per page")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": 200,
                "message": "Success",
                "data": [],
                "total": 0,
                "page": 1,
                "limit": 100,
                "timestamp": "2025-06-30T12:00:00Z"
            }
        }

class CreatedResponse(BaseResponse):
    """Created response model (201)"""
    data: Any = Field(..., description="Created resource data")
    resource_id: Optional[Union[int, str]] = Field(None, description="Created resource ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": 201,
                "message": "Resource created successfully",
                "data": {},
                "resource_id": 1,
                "timestamp": "2025-06-30T12:00:00Z"
            }
        }

class DeletedResponse(BaseResponse):
    """Deleted response model (204 content)"""
    resource_id: Optional[Union[int, str]] = Field(None, description="Deleted resource ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": 204,
                "message": "Resource deleted successfully",
                "resource_id": 1,
                "timestamp": "2025-06-30T12:00:00Z"
            }
        }

# Common response templates
def success_response(data: Any = None, message: str = "Success", status: int = 200) -> dict:
    """Generate a success response dictionary"""
    return {
        "status": status,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow()
    }

def error_response(message: str, status: int = 400, error_code: str = None, details: dict = None) -> dict:
    """Generate an error response dictionary"""
    response = {
        "status": status,
        "message": message,
        "timestamp": datetime.utcnow()
    }
    if error_code:
        response["error_code"] = error_code
    if details:
        response["details"] = details
    return response

def list_response(data: List[Any], total: int = None, page: int = 1, limit: int = 100, message: str = "Success") -> dict:
    """Generate a list response dictionary"""
    return {
        "status": 200,
        "message": message,
        "data": data,
        "total": total if total is not None else len(data),
        "page": page,
        "limit": limit,
        "timestamp": datetime.utcnow()
    }

def created_response(data: Any, resource_id: Union[int, str] = None, message: str = "Resource created successfully") -> dict:
    """Generate a created response dictionary"""
    response = {
        "status": 201,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow()
    }
    if resource_id:
        response["resource_id"] = resource_id
    return response

def deleted_response(resource_id: Union[int, str] = None, message: str = "Resource deleted successfully") -> dict:
    """Generate a deleted response dictionary"""
    response = {
        "status": 204,
        "message": message,
        "timestamp": datetime.utcnow()
    }
    if resource_id:
        response["resource_id"] = resource_id
    return response 