from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List

from app.db.sql import get_db
from app.models.file import File 
from app.models.image import Image 
from app.schemas.image import ImageOut, ImageCreate, ImageUpdate, ImageUploadResponse, ImageListResponse

router = APIRouter()

@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = FastAPIFile(...),
    description: Optional[str] = None,
    alt_text: Optional[str] = None,
    order: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
  
    try:
        # Create file record
        file_record = await File.build_by_field_storage_v2(file)
        db.add(file_record)
        await db.commit()
        await db.refresh(file_record)
        
        # Create image record using build method
        image = Image.build_from_form(
            filename=getattr(file_record, 'filename', 'unknown') or "unknown",
            image_url=getattr(file_record, 'public_url', '') or "",
            backup_image_url=getattr(file_record, 'public_url', None),
            description=description,
            order=order or 0,
            file_id=getattr(file_record, 'id', None),
        )
        db.add(image)
        await db.commit()
        await db.refresh(image)
        
        # Return structured upload response
        return ImageUploadResponse(
            image=ImageOut.model_validate(image),
            message="Image uploaded successfully"
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File upload failed: {str(e)}"
        )

@router.get("/", response_model=ImageListResponse)
async def get_images(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all images with pagination
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: Whether to return only non-deleted images
        db: Async database session
        
    Returns:
        ImageListResponse: List of images with pagination
    """
    try:
        # Build query
        query = select(Image)
        count_query = select(func.count(Image.id))
        
        if active_only:
            query = query.where(Image.is_deleted == False)
            count_query = count_query.where(Image.is_deleted == False)
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Image.order, Image.id)
        
        result = await db.execute(query)
        images = result.scalars().all()
        
        # Convert to ImageOut schemas
        images_data = [ImageOut.model_validate(image) for image in images]
        
        return ImageListResponse(
            images=images_data,
            total=total,
            page=(skip // limit) + 1 if limit > 0 else 1,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve images: {str(e)}"
        )

@router.get("/{image_id}", response_model=ImageOut)
async def get_image(
    image_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get image by ID
    
    Args:
        image_id: Image ID
        db: Async database session
        
    Returns:
        ImageOut: Image data
        
    Raises:
        HTTPException: If image not found
    """
    try:
        result = await db.execute(select(Image).where(Image.id == image_id))
        image = result.scalar_one_or_none()
        
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        return ImageOut.model_validate(image)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve image: {str(e)}"
        )

@router.put("/{image_id}", response_model=ImageOut)
async def update_image(
    image_id: int,
    image_update: ImageUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update image by ID
    
    Args:
        image_id: Image ID
        image_update: Image update data
        db: Async database session
        
    Returns:
        ImageOut: Updated image data
        
    Raises:
        HTTPException: If image not found or update fails
    """
    try:
        result = await db.execute(select(Image).where(Image.id == image_id))
        image = result.scalar_one_or_none()
        
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        # Update fields that are provided
        update_data = image_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(image, field, value)
        
        await db.commit()
        await db.refresh(image)
        
        return ImageOut.model_validate(image)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update image: {str(e)}"
        )

@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete an image (mark as deleted)
    
    Args:
        image_id: Image ID
        db: Async database session
        
    Raises:
        HTTPException: If image not found
    """
    try:
        result = await db.execute(select(Image).where(Image.id == image_id))
        image = result.scalar_one_or_none()
        
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        # Soft delete
        setattr(image, 'is_deleted', True)
        db.add(image)
        await db.commit()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete image: {str(e)}"
        )
