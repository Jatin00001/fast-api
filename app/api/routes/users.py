from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List

from app.db.sql import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate, UserListResponse
from app.core.security import get_password_hash
import logging

router = APIRouter()
logger = logging.getLogger("api")

@router.get("/", response_model=UserListResponse)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all users with optional filtering and pagination
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Search term for username or email
        is_active: Filter by active status
        db: Async database session
        
    Returns:
        UserListResponse: List of users with pagination information
    """
    logger.info(f"Fetching users - skip: {skip}, limit: {limit}, search: {search}, is_active: {is_active}")
    
    try:
        # Build query
        query = select(User)
        count_query = select(func.count(User.id))
        
        # Apply filters
        if search:
            search_filter = User.username.ilike(f"%{search}%") | User.email.ilike(f"%{search}%")
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
            
        if is_active is not None:
            query = query.where(User.is_active == is_active)
            count_query = count_query.where(User.is_active == is_active)
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination and execute
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await db.execute(query)
        users = result.scalars().all()
        
        # Convert to UserOut schemas
        users_data = [UserOut.model_validate(user) for user in users]
        
        logger.info(f"Successfully retrieved {len(users)} users")
        
        return UserListResponse(
            users=users_data,
            total=total,
            page=(skip // limit) + 1 if limit > 0 else 1,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to retrieve users",
                "error_code": "DATABASE_ERROR",
                "details": {"error": str(e)}
            }
        )

@router.post("/", response_model=UserOut, status_code=201)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create new user
    
    Args:
        user_in: User creation data
        db: Async database session
        
    Returns:
        UserOut: Created user information
    """
    logger.info(f"Creating new user with email: {user_in.email}")
    
    try:
        # Check if email already exists
        result = await db.execute(
            select(User).where(User.email == user_in.email)
        )
        if result.scalar_one_or_none():
            logger.warning(f"Attempt to create user with existing email: {user_in.email}")
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Email already registered",
                    "error_code": "EMAIL_EXISTS",
                    "details": {"email": user_in.email}
                }
            )
        
        # Check if username already exists
        result = await db.execute(
            select(User).where(User.username == user_in.username)
        )
        if result.scalar_one_or_none():
            logger.warning(f"Attempt to create user with existing username: {user_in.username}")
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Username already taken",
                    "error_code": "USERNAME_EXISTS",
                    "details": {"username": user_in.username}
                }
            )
        
        # Create new user using build method
        user = User.build_from_form(
            email=user_in.email,
            username=user_in.username,
            hashed_password=get_password_hash(user_in.password),
            is_active=user_in.is_active,
            is_superuser=user_in.is_superuser,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"Successfully created user with ID: {user.id}")
        
        return UserOut.model_validate(user)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to create user",
                "error_code": "USER_CREATION_ERROR",
                "details": {"error": str(e)}
            }
        )

@router.get("/{user_id}", response_model=UserOut)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get user by ID
    
    Args:
        user_id: User ID
        db: Async database session
        
    Returns:
        UserOut: User data
    """
    logger.info(f"Fetching user with ID: {user_id}")
    
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"User with ID {user_id} not found")
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "User not found",
                    "error_code": "USER_NOT_FOUND",
                    "details": {"user_id": user_id}
                }
            )
        
        logger.info(f"Successfully retrieved user: {user.username}")
        return UserOut.model_validate(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to retrieve user",
                "error_code": "DATABASE_ERROR",
                "details": {"error": str(e)}
            }
        )

@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update user by ID
    
    Args:
        user_id: User ID
        user_update: User update data
        db: Async database session
        
    Returns:
        UserOut: Updated user data
    """
    logger.info(f"Updating user with ID: {user_id}")
    
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"User with ID {user_id} not found for update")
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "User not found",
                    "error_code": "USER_NOT_FOUND",
                    "details": {"user_id": user_id}
                }
            )
        
        # Update fields that are provided
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Handle password update
        if 'password' in update_data:
            update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"Successfully updated user: {user.username}")
        return UserOut.model_validate(user)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to update user",
                "error_code": "USER_UPDATE_ERROR",
                "details": {"error": str(e)}
            }
        )

@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete user by ID
    
    Args:
        user_id: User ID
        db: Async database session
        
    Returns:
        None: 204 No Content on successful deletion
    """
    logger.info(f"Deleting user with ID: {user_id}")
    
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"User with ID {user_id} not found for deletion")
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "User not found",
                    "error_code": "USER_NOT_FOUND",
                    "details": {"user_id": user_id}
                }
            )
        
        await db.delete(user)
        await db.commit()
        
        logger.info(f"Successfully deleted user: {user.username}")
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to delete user",
                "error_code": "USER_DELETION_ERROR",
                "details": {"error": str(e)}
            }
        )