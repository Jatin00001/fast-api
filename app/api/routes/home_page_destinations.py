from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File as FastAPIFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.db.sql import get_db
from app.models.file import File
from app.models.home_destination import HomePageDestinations
from app.schemas.home_destination import HomeDestinationOut, HomeDestinationCreate, HomeDestinationUpdate, HomeDestinationListResponse
import logging

router = APIRouter()
logger = logging.getLogger("api")

@router.post("/", response_model=HomeDestinationOut)
async def create_home_destination(
    city: str = Form(...),
    order: int = Form(...),
    is_active: bool = Form(False),
    file: UploadFile = FastAPIFile(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new home page destination with image upload
    
    Args:
        city: City name (required)
        order: Display order, must be unique (required)
        is_active: Whether the destination is active (default: False)
        file: Image file to upload (required)
        db: Async database session
        
    Returns:
        HomeDestinationOut: Created destination data
    """
    
    try:
        # Validate order range
        if not (1 <= order <= 999):
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Invalid order value",
                    "error_code": "INVALID_ORDER",
                    "details": {"order": order, "valid_range": "1-999"}
                }
            )
        
        # Check if order already exists
        result_query = await db.execute(
            select(HomePageDestinations).where(HomePageDestinations.order == order)
        )
        existing = result_query.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": f"Home destination with order {order} already exists",
                    "error_code": "ORDER_EXISTS",
                    "details": {"order": order, "existing_id": existing.id}
                }
            )
        
        # Validate file
        if not file or not file.filename:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Image file is required",
                    "error_code": "FILE_REQUIRED",
                    "details": {"file_provided": bool(file)}
                }
            )
        
        # Upload file and create file record
        logger.info(f"Uploading file: {file.filename}")
        try:
            file_record = await File.build_by_field_storage_v2(file)
            db.add(file_record)
            await db.commit()
            await db.refresh(file_record)
            logger.info(f"File uploaded successfully: {file_record.public_url}")
        except Exception as e:
            await db.rollback()
            logger.error(f"File upload failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Failed to upload image file",
                    "error_code": "FILE_UPLOAD_ERROR",
                    "details": {"error": str(e)}
                }
            )
        
        # Create home destination
        destination = HomePageDestinations.build(
            city=city,
            order=order,
            is_active=is_active,
            image=file_record.id,
            image_url=file_record.public_url,
        )
        
        db.add(destination)
        await db.commit()
        await db.refresh(destination)
        
        logger.info(f"Home destination created successfully: ID {destination.id}")
        return HomeDestinationOut.model_validate(destination)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create home destination: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to create home destination",
                "error_code": "CREATION_ERROR",
                "details": {"error": str(e)}
            }
        )

@router.get("/", response_model=HomeDestinationListResponse)
async def get_home_destinations(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all home page destinations with filtering and pagination
    
    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)
        active_only: Whether to return only active destinations (default: True)
        search: Search term for city name (optional)
        db: Async database session
        
    Returns:
        HomeDestinationListResponse: List of destinations with pagination
    """
    
    try:
        # Build query
        query = select(HomePageDestinations)
        count_query = select(func.count(HomePageDestinations.id))
        
        # Apply filters
        if active_only:
            query = query.where(HomePageDestinations.is_active == True)
            count_query = count_query.where(HomePageDestinations.is_active == True)
            
        if search:
            search_filter = HomePageDestinations.city.ilike(f"%{search}%")
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination and execute
        query = query.offset(skip).limit(limit).order_by(HomePageDestinations.order)
        result_query = await db.execute(query)
        destinations = result_query.scalars().all()
        
        # Convert to schema objects
        destinations_data = [HomeDestinationOut.model_validate(dest) for dest in destinations]
        
        logger.info(f"Retrieved {len(destinations)} home destinations")
        
        return HomeDestinationListResponse(
            destinations=destinations_data,
            total=total,
            active_count=len([d for d in destinations_data if d.is_active])
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve home destinations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to retrieve home destinations",
                "error_code": "RETRIEVAL_ERROR",
                "details": {"error": str(e)}
            }
        )

@router.get("/{destination_id}", response_model=HomeDestinationOut)
async def get_home_destination(
    destination_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get home page destination by ID
    
    Args:
        destination_id: Destination ID
        db: Async database session
        
    Returns:
        HomeDestinationOut: Destination data
    """
    
    try:
        result_query = await db.execute(
            select(HomePageDestinations).where(HomePageDestinations.id == destination_id)
        )
        destination = result_query.scalar_one_or_none()
        
        if not destination:
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "Home destination not found",
                    "error_code": "DESTINATION_NOT_FOUND",
                    "details": {"destination_id": destination_id}
                }
            )
        
        logger.info(f"Retrieved home destination: ID {destination.id}")
        return HomeDestinationOut.model_validate(destination)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve home destination {destination_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to retrieve home destination",
                "error_code": "RETRIEVAL_ERROR",
                "details": {"destination_id": destination_id, "error": str(e)}
            }
        )

@router.put("/{destination_id}", response_model=HomeDestinationOut)
async def update_home_destination(
    destination_id: int,
    city: Optional[str] = Form(None),
    order: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(None),
    file: Optional[UploadFile] = FastAPIFile(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing home destination
    
    Args:
        destination_id: Home destination ID
        city: Updated city name (optional)
        order: Updated display order (optional)
        is_active: Updated active status (optional)
        file: New image file (optional)
        db: Async database session
        
    Returns:
        HomeDestinationOut: Updated home destination data
    """
    logger.info(f"Updating home destination with ID: {destination_id}")
    
    try:
        # Check if destination exists
        result_query = await db.execute(select(HomePageDestinations).where(HomePageDestinations.id == destination_id))
        destination = result_query.scalar_one_or_none()
        
        if not destination:
            logger.warning(f"Home destination with ID {destination_id} not found")
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "Home destination not found",
                    "error_code": "DESTINATION_NOT_FOUND",
                    "details": {"destination_id": destination_id}
                }
            )
        
        # Check if order is being changed and if it would conflict
        if order is not None and order != destination.order:
            result_query = await db.execute(select(HomePageDestinations).where(
                HomePageDestinations.order == order,
                HomePageDestinations.id != destination_id
            ))
            existing = result_query.scalar_one_or_none()
            if existing:
                logger.warning(f"Attempt to update destination with existing order: {order}")
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": f"Another destination with order {order} already exists",
                        "error_code": "ORDER_CONFLICT",
                        "details": {"order": order, "existing_id": existing.id}
                    }
                )
        
        # Handle file upload if provided
        image_id = None
        if file and file.filename:
            try:
                # Upload file and get file record
                uploaded_file = await File.build_by_field_storage_v2(file)
                if uploaded_file:
                    image_id = uploaded_file.id
                    logger.info(f"New image uploaded with ID: {image_id}")
            except Exception as upload_error:
                logger.error(f"Error uploading image: {str(upload_error)}")
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": "Failed to upload image",
                        "error_code": "IMAGE_UPLOAD_ERROR",
                        "details": {"error": str(upload_error)}
                    }
                )
        
        # Prepare update data
        update_data = {}
        if city is not None:
            update_data['city'] = city.lower()  # Normalize city name
        if order is not None:
            update_data['order'] = order
        if is_active is not None:
            update_data['is_active'] = is_active
        if image_id is not None:
            update_data['image'] = image_id
        
        # Update fields manually since HomePageDestinations doesn't have update method
        for field, value in update_data.items():
            setattr(destination, field, value)
        
        db.add(destination)
        await db.commit()
        await db.refresh(destination)
        
        logger.info(f"Home destination {destination_id} updated successfully")
        return HomeDestinationOut.model_validate(destination)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating destination {destination_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to update home destination",
                "error_code": "UPDATE_ERROR",
                "details": {"error": str(e)}
            }
        )

@router.delete("/{destination_id}")
async def delete_home_destination(
    destination_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete home page destination
    
    Args:
        destination_id: Destination ID
        db: Async database session
        
    Returns:
        dict: Success message
    """
    
    try:
        # Get existing destination
        result_query = await db.execute(
            select(HomePageDestinations).where(HomePageDestinations.id == destination_id)
        )
        destination = result_query.scalar_one_or_none()
        
        if not destination:
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "Home destination not found",
                    "error_code": "DESTINATION_NOT_FOUND",
                    "details": {"destination_id": destination_id}
                }
            )
        
        # Delete the destination
        await db.delete(destination)
        await db.commit()
        
        logger.info(f"Home destination {destination_id} deleted successfully")
        
        return {
            "message": "Home destination deleted successfully",
            "destination_id": destination_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete home destination {destination_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to delete home destination",
                "error_code": "DELETE_ERROR",
                "details": {"destination_id": destination_id, "error": str(e)}
            }
        )