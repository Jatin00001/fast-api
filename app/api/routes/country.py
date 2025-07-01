from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from app.db.sql import get_db
from app.models.country import Country
from app.schemas.country import CountryOut, CountryCreate, CountryUpdate, CountryListResponse
import logging

router = APIRouter()
logger = logging.getLogger("api")

@router.post("/", response_model=CountryOut)
async def create_country(
    name: str = Form(...),
    slug: str = Form(...),
    showon_destmenu: bool = Form(False),
    country_code: str = Form(...),
    location: Optional[str] = Form(None),
    image_id: Optional[int] = Form(None),
    image_url: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new country
    
    Args:
        name: Country name
        slug: Country slug (unique identifier)
        showon_destmenu: Whether to show on destination menu
        country_code: ISO country code
        location: Geographic location description
        image_id: Associated image ID
        image_url: Image URL
        db: Async database session
        
    Returns:
        CountryOut: Created country information
    """
    logger.info(f"Creating new country: {name} with code: {country_code}")
    
    try:
        country_data = Country.build_from_form(
            name=name,
            slug=slug,
            country_code=country_code,
            showon_destmenu=showon_destmenu,
            location=location,
            image_id=image_id,
            image_url=image_url,
        )

        # Check if country already exists
        existing = await Country.get_by_code(db, code=country_code)
        if existing:
            logger.warning(f"Attempt to create country with existing code: {country_code}")
            raise HTTPException(
                status_code=400,
                detail={
                    "message": f"Country with code '{country_code}' already exists",
                    "error_code": "COUNTRY_CODE_EXISTS",
                    "details": {"country_code": country_code, "existing_id": existing.id}
                }
            )

        # Check if slug already exists
        result = await db.execute(select(Country).where(Country.slug == slug))
        existing_slug = result.scalar_one_or_none()
        if existing_slug:
            logger.warning(f"Attempt to create country with existing slug: {slug}")
            raise HTTPException(
                status_code=400,
                detail={
                    "message": f"Country with slug '{slug}' already exists",
                    "error_code": "COUNTRY_SLUG_EXISTS",
                    "details": {"slug": slug, "existing_id": existing_slug.id}
                }
            )

        # Create country using built object
        db.add(country_data)
        await db.commit()
        await db.refresh(country_data)
        
        logger.info(f"Successfully created country: {name} with ID: {country_data.id}")
        
        return CountryOut.model_validate(country_data)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating country {name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to create country",
                "error_code": "COUNTRY_CREATION_ERROR",
                "details": {"error": str(e)}
            }
        )

@router.get("/", response_model=CountryListResponse)
async def get_countries(
    skip: int = 0,
    limit: int = 100,
    showon_destmenu: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all countries with optional filtering and pagination
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        showon_destmenu: Filter by destination menu visibility
        search: Search term for country name
        db: Async database session
        
    Returns:
        CountryListResponse: List of countries with pagination information
    """
    logger.info(f"Fetching countries - skip: {skip}, limit: {limit}, showon_destmenu: {showon_destmenu}, search: {search}")
    
    try:
        # Build query
        query = select(Country)
        count_query = select(func.count(Country.id))
        
        # Apply filters
        if showon_destmenu is not None:
            query = query.where(Country.showon_destmenu == showon_destmenu)
            count_query = count_query.where(Country.showon_destmenu == showon_destmenu)
            
        if search:
            search_filter = Country.name.ilike(f"%{search}%")
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination and execute
        query = query.offset(skip).limit(limit).order_by(Country.created_at.desc())
        result = await db.execute(query)
        countries = result.scalars().all()
        
        # Convert to CountryOut schemas
        countries_data = [CountryOut.model_validate(country) for country in countries]
        
        logger.info(f"Successfully retrieved {len(countries)} countries")
        
        return CountryListResponse(
            countries=countries_data,
            total=total,
            page=(skip // limit) + 1 if limit > 0 else 1,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error fetching countries: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to retrieve countries",
                "error_code": "DATABASE_ERROR",
                "details": {"error": str(e)}
            }
        )

@router.get("/{country_id}", response_model=CountryOut)
async def get_country(
    country_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get country by ID
    
    Args:
        country_id: Country ID
        db: Async database session
        
    Returns:
        CountryOut: Country data
    """
    logger.info(f"Fetching country with ID: {country_id}")
    
    try:
        result = await db.execute(select(Country).where(Country.id == country_id))
        country = result.scalar_one_or_none()
        
        if not country:
            logger.warning(f"Country with ID {country_id} not found")
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "Country not found",
                    "error_code": "COUNTRY_NOT_FOUND",
                    "details": {"country_id": country_id}
                }
            )
        
        logger.info(f"Successfully retrieved country: {country.name}")
        return CountryOut.model_validate(country)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching country {country_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to retrieve country",
                "error_code": "DATABASE_ERROR",
                "details": {"error": str(e)}
            }
        )

@router.get("/slug/{slug}", response_model=CountryOut)
async def get_country_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get country by slug
    
    Args:
        slug: Country slug
        db: Async database session
        
    Returns:
        CountryOut: Country data
    """
    logger.info(f"Fetching country with slug: {slug}")
    
    try:
        result = await db.execute(select(Country).where(Country.slug == slug))
        country = result.scalar_one_or_none()
        
        if not country:
            logger.warning(f"Country with slug {slug} not found")
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "Country not found",
                    "error_code": "COUNTRY_NOT_FOUND",
                    "details": {"slug": slug}
                }
            )
        
        logger.info(f"Successfully retrieved country: {country.name}")
        return CountryOut.model_validate(country)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching country by slug {slug}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to retrieve country",
                "error_code": "DATABASE_ERROR",
                "details": {"error": str(e)}
            }
        )

@router.put("/{country_id}", response_model=CountryOut)
async def update_country(
    country_id: int,
    country_update: CountryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update country by ID
    
    Args:
        country_id: Country ID
        country_update: Country update data
        db: Async database session
        
    Returns:
        CountryOut: Updated country data
    """
    logger.info(f"Updating country with ID: {country_id}")
    
    try:
        result = await db.execute(select(Country).where(Country.id == country_id))
        country = result.scalar_one_or_none()
        
        if not country:
            logger.warning(f"Country with ID {country_id} not found for update")
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "Country not found",
                    "error_code": "COUNTRY_NOT_FOUND",
                    "details": {"country_id": country_id}
                }
            )
        
        # Update fields that are provided
        update_data = country_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(country, field, value)
        
        await db.commit()
        await db.refresh(country)
        
        logger.info(f"Successfully updated country: {country.name}")
        return CountryOut.model_validate(country)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating country {country_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to update country",
                "error_code": "COUNTRY_UPDATE_ERROR",
                "details": {"error": str(e)}
            }
        )

@router.delete("/{country_id}", status_code=204)
async def delete_country(
    country_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete country by ID
    
    Args:
        country_id: Country ID
        db: Async database session
        
    Returns:
        None: 204 No Content on successful deletion
    """
    logger.info(f"Deleting country with ID: {country_id}")
    
    try:
        result = await db.execute(select(Country).where(Country.id == country_id))
        country = result.scalar_one_or_none()
        
        if not country:
            logger.warning(f"Country with ID {country_id} not found for deletion")
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "Country not found",
                    "error_code": "COUNTRY_NOT_FOUND",
                    "details": {"country_id": country_id}
                }
            )
        
        await db.delete(country)
        await db.commit()
        
        logger.info(f"Successfully deleted country: {country.name}")
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting country {country_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to delete country",
                "error_code": "COUNTRY_DELETION_ERROR",
                "details": {"error": str(e)}
            }
        )
