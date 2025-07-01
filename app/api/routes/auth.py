from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.db.sql import get_db
from app.models.user import User
from app.schemas.user import TokenResponse
from app.schemas.response import success_response, error_response
import logging

router = APIRouter()
logger = logging.getLogger("api")

@router.post("/login")
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    OAuth2 compatible token login, get an access token for future requests
    
    Args:
        form_data: OAuth2 password request form data
        db: Async database session
        
    Returns:
        dict: Access token and token type
    """
    logger.info(f"Login attempt for user: {form_data.username}")
    
    try:
        # Query user by email
        result = await db.execute(
            select(User).where(User.email == form_data.username)
        )
        user = result.scalar_one_or_none()
        
        # Verify user exists and password is correct
        if not user or not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Failed login attempt for user: {form_data.username} - Invalid credentials")
            
            response.status_code = 401
            return error_response(
                message="Incorrect email or password",
                status=401,
                error_code="INVALID_CREDENTIALS",
                details={"username": form_data.username}
            )
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Failed login attempt for inactive user: {form_data.username}")
            response.status_code = 401
            return error_response(
                message="Inactive user account",
                status=401,
                error_code="INACTIVE_USER",
                details={"username": form_data.username}
            )
        
        # Generate access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            subject=str(user.id),
            expires_delta=access_token_expires
        )
        
        logger.info(f"Successful login for user: {form_data.username} (ID: {user.id})")
        
        response.status_code = 200
        return success_response(
            data={
                "access_token": token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_active": user.is_active,
                    "is_superuser": user.is_superuser
                }
            },
            message="Login successful"
        )
        
    except Exception as e:
        logger.error(f"Login error for user {form_data.username}: {str(e)}")
        
        response.status_code = 500
        return error_response(
            message="An error occurred while processing your request",
            status=500,
            error_code="LOGIN_ERROR",
            details={"error": str(e)}
        )