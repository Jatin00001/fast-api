from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.db.sql import get_db
from app.models.file import File
from app.services.aws_service import aws_service
from app.services.gcp_service import gcp_service

router = APIRouter()

@router.post("/upload/gcp", status_code=status.HTTP_201_CREATED)
async def upload_file_to_gcp(
    file: UploadFile = FastAPIFile(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload file to Google Cloud Storage
    
    Args:
        file: File to upload
        db: Async database session
        
    Returns:
        Upload result with file information
        
    Raises:
        HTTPException: If file type not allowed or upload fails
    """
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Only JPEG, PNG, GIF, or WebP images are allowed"
        )

    try:
        # Generate unique filename
        filename = f"{uuid.uuid4().hex}_{file.filename}"

        # Upload to GCP
        result = await gcp_service.upload_file(
            file_obj=file.file,
            object_name=filename,
            content_type=file.content_type
        )

        return {
            "message": "File uploaded successfully to GCP",
            "filename": filename,
            "url": result.get("public_url"),
            "blob_name": result.get("blob_name")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )

@router.post("/upload/file-record", status_code=status.HTTP_201_CREATED)
async def create_file_record(
    file: UploadFile = FastAPIFile(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload file and create a database record
    
    Args:
        file: File to upload
        db: Async database session
        
    Returns:
        Created file record information
        
    Raises:
        HTTPException: If file type not allowed or upload fails
    """
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, GIF, or WebP images are allowed"
        )

    try:
        # Build File object and upload
        file_obj = await File.build_by_field_storage_v2(file)
        
        # Save to database
        db.add(file_obj)
        await db.commit()
        await db.refresh(file_obj)
        
        return {
            "message": "File uploaded and record created successfully",
            "file_id": file_obj.id,
            "filename": file_obj.filename,
            "identifier": file_obj.identifier,
            "public_url": file_obj.public_url,
            "blob_name": file_obj.blob_name,
            "size": file_obj.size
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )

@router.post("/upload/aws", status_code=status.HTTP_201_CREATED)
async def upload_file_to_aws(
    file: UploadFile = FastAPIFile(...),
):
    """
    Upload file to AWS S3
    
    Args:
        file: File to upload
        
    Returns:
        Upload result with file information
        
    Raises:
        HTTPException: If file type not allowed or upload fails
    """
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, GIF, or WebP images are allowed"
        )

    try:
        # Generate unique filename
        filename = f"{uuid.uuid4().hex}_{file.filename}"

        # Upload to AWS S3
        result = aws_service.upload_file(
            file_obj=file.file,
            object_name=filename,
            content_type=file.content_type
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Upload failed: {result.get('error', 'Unknown error')}"
        )

        return {
            "message": "File uploaded successfully to AWS S3",
            "filename": filename,
            "url": result.get("url")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )
