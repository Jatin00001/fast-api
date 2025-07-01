from typing import Annotated, AsyncGenerator

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_token_payload
from app.db.sql import get_db
from app.models.user import User
from app.schemas.user import TokenPayload

async def get_current_user(
    token: Annotated[TokenPayload, Depends(get_current_token_payload)],
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current authenticated user
    
    Args:
        token: Validated token payload
        db: Database session
        
    Returns:
        Current user model
        
    Raises:
        HTTPException: If user not found or inactive
    """
    try:
        result = await db.execute(
            select(User).where(User.id == int(token.sub))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
            
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not get current user"
        ) from e

async def get_current_active_superuser(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Get the current authenticated superuser
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current superuser model
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentSuperUser = Annotated[User, Depends(get_current_active_superuser)]