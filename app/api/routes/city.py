from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from app.db.sql import get_db
from app.models.city import City
from app.models.country import Country
from app.schemas.city import CityOut, CityCreate, CityUpdate, CityListResponse
import logging

router = APIRouter()
logger = logging.getLogger("api")

@router.post("/", response_model=CityOut)
async def create_city(
    city: CityCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new city"""
    logger.info(f"Creating new city: {city.name} with slug: {city.slug}")
    
    try:
        # Validate foreign key: Check if country exists
        if city.country_id:
            country_result = await db.execute(select(Country).where(Country.id == city.country_id))
            if not country_result.scalar_one_or_none():
                logger.warning(f"Attempt to create city with non-existent country_id: {city.country_id}")
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": f"Country with ID {city.country_id} does not exist",
                        "error_code": "COUNTRY_NOT_FOUND",
                        "details": {"country_id": city.country_id}
                    }
                )
        
        # Check if city with slug already exists
        result = await db.execute(select(City).where(City.slug == city.slug))
        existing = result.scalar_one_or_none()
        if existing:
            logger.warning(f"Attempt to create city with existing slug: {city.slug}")
            raise HTTPException(
                status_code=400,
                detail={
                    "message": f"City with slug '{city.slug}' already exists",
                    "error_code": "CITY_SLUG_EXISTS",
                    "details": {"slug": city.slug, "existing_id": existing.id}
                }
            )
        
        # Create new city using build method
        new_city = City.build_from_form(
            name=city.name,
            slug=city.slug,
            country_id=city.country_id,
            is_active=city.is_active,
            image_id=city.image_id,
            image_url=city.image_url,
            order=city.order,
        )
        db.add(new_city)
        await db.commit()
        await db.refresh(new_city)
        
        logger.info(f"Successfully created city: {city.name} with ID: {new_city.id}")
        
        return CityOut.model_validate(new_city)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating city {city.name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to create city",
                "error_code": "CITY_CREATION_ERROR",
                "details": {"error": str(e)}
            }
        )

@router.get("/", response_model=CityListResponse)
async def get_cities(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    country_id: Optional[int] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all cities with optional filtering and pagination"""
    logger.info(f"Fetching cities - skip: {skip}, limit: {limit}, is_active: {is_active}, country_id: {country_id}, search: {search}")
    
    try:
        # Build query
        query = select(City)
        count_query = select(func.count(City.id))
        
        # Apply filters
        if is_active is not None:
            query = query.where(City.is_active == is_active)
            count_query = count_query.where(City.is_active == is_active)
            
        if country_id is not None:
            query = query.where(City.country_id == country_id)
            count_query = count_query.where(City.country_id == country_id)
            
        if search:
            search_filter = City.name.ilike(f"%{search}%")
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination and execute
        query = query.offset(skip).limit(limit).order_by(City.order.asc(), City.created_at.desc())
        result = await db.execute(query)
        cities = result.scalars().all()
        
        # Convert to CityOut schemas
        cities_data = [CityOut.model_validate(city) for city in cities]
        
        logger.info(f"Successfully retrieved {len(cities)} cities")
        
        return CityListResponse(
            cities=cities_data,
            total=total,
            page=(skip // limit) + 1 if limit > 0 else 1,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error fetching cities: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to retrieve cities",
                "error_code": "DATABASE_ERROR",
                "details": {"error": str(e)}
            }
        )

@router.get("/{city_id}", response_model=CityOut)
async def get_city(
    city_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get city by ID"""
    logger.info(f"Fetching city with ID: {city_id}")
    
    try:
        result = await db.execute(select(City).where(City.id == city_id))
        city = result.scalar_one_or_none()
        
        if not city:
            logger.warning(f"City with ID {city_id} not found")
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "City not found",
                    "error_code": "CITY_NOT_FOUND",
                    "details": {"city_id": city_id}
                }
            )
        
        logger.info(f"Successfully retrieved city: {city.name}")
        return CityOut.model_validate(city)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching city {city_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to retrieve city",
                "error_code": "DATABASE_ERROR",
                "details": {"error": str(e)}
            }
        )

@router.get("/slug/{slug}", response_model=CityOut)
async def get_city_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Get city by slug"""
    logger.info(f"Fetching city with slug: {slug}")
    
    try:
        result = await db.execute(select(City).where(City.slug == slug))
        city = result.scalar_one_or_none()
        
        if not city:
            logger.warning(f"City with slug {slug} not found")
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "City not found",
                    "error_code": "CITY_NOT_FOUND",
                    "details": {"slug": slug}
                }
            )
        
        logger.info(f"Successfully retrieved city: {city.name}")
        return CityOut.model_validate(city)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching city by slug {slug}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to retrieve city",
                "error_code": "DATABASE_ERROR",
                "details": {"error": str(e)}
            }
        )

@router.put("/{city_id}", response_model=CityOut)
async def update_city(
    city_id: int,
    city_update: CityUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing city"""
    logger.info(f"Updating city with ID: {city_id}")
    
    try:
        result = await db.execute(select(City).where(City.id == city_id))
        city = result.scalar_one_or_none()
        
        if not city:
            logger.warning(f"City with ID {city_id} not found for update")
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "City not found",
                    "error_code": "CITY_NOT_FOUND",
                    "details": {"city_id": city_id}
                }
            )
        
        # Validate country_id if being updated
        update_data = city_update.model_dump(exclude_unset=True)
        if 'country_id' in update_data and update_data['country_id']:
            country_result = await db.execute(select(Country).where(Country.id == update_data['country_id']))
            if not country_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": f"Country with ID {update_data['country_id']} does not exist",
                        "error_code": "COUNTRY_NOT_FOUND",
                        "details": {"country_id": update_data['country_id']}
                    }
                )
        
        # Update fields that are provided
        for field, value in update_data.items():
            setattr(city, field, value)
        
        await db.commit()
        await db.refresh(city)
        
        logger.info(f"Successfully updated city: {city.name}")
        return CityOut.model_validate(city)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating city {city_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to update city",
                "error_code": "CITY_UPDATE_ERROR",
                "details": {"error": str(e)}
            }
        )

@router.delete("/{city_id}", status_code=204)
async def delete_city(
    city_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a city"""
    logger.info(f"Deleting city with ID: {city_id}")
    
    try:
        result = await db.execute(select(City).where(City.id == city_id))
        city = result.scalar_one_or_none()
        
        if not city:
            logger.warning(f"City with ID {city_id} not found for deletion")
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "City not found",
                    "error_code": "CITY_NOT_FOUND",
                    "details": {"city_id": city_id}
                }
            )
        
        await db.delete(city)
        await db.commit()
        
        logger.info(f"Successfully deleted city: {city.name}")
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting city {city_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to delete city",
                "error_code": "CITY_DELETION_ERROR",
                "details": {"error": str(e)}
            }
        )
