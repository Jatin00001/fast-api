from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from typing import Optional

from app.db.sql import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ✅ Build Methods
    @classmethod
    def build_from_form(
        cls,
        email: str,
        username: str,
        hashed_password: str,
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> "User":
        """
        Build a User instance from form data
        
        Args:
            email: User email address
            username: Username
            hashed_password: Hashed password
            is_active: Whether user is active
            is_superuser: Whether user has admin privileges
            
        Returns:
            User: New user instance
        """
        return cls.build(
            email=email,
            username=username,
            hashed_password=hashed_password,
            is_active=is_active,
            is_superuser=is_superuser,
        )

    @classmethod
    def build(
        cls,
        email: str,
        username: str,
        hashed_password: str,
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> "User":
        """
        Build a User instance with business logic and validation
        
        Args:
            email: User email address
            username: Username  
            hashed_password: Hashed password
            is_active: Whether user is active
            is_superuser: Whether user has admin privileges
            
        Returns:
            User: New user instance with validated data
        """
        # Normalize email and username
        email = email.lower().strip() if email else email
        username = username.lower().strip() if username else username
        
        return cls(
            email=email,
            username=username,
            hashed_password=hashed_password,
            is_active=is_active,
            is_superuser=is_superuser
        )

    @classmethod
    def build_from_oauth(
        cls,
        email: str,
        username: Optional[str] = None,
        is_active: bool = True,
    ) -> "User":
        """
        Build a User instance from OAuth data (no password required)
        
        Args:
            email: User email address
            username: Username (generated from email if not provided)
            is_active: Whether user is active
            
        Returns:
            User: New user instance
        """
        if not username:
            # Generate username from email
            username = email.split('@')[0].lower()
        
        return cls.build(
            email=email,
            username=username,
            hashed_password="",  # OAuth users don't have passwords
            is_active=is_active,
            is_superuser=False
        )

    @classmethod
    def build_admin(
        cls,
        email: str,
        username: str,
        hashed_password: str,
    ) -> "User":
        """
        Build an admin User instance
        
        Args:
            email: Admin email address
            username: Admin username
            hashed_password: Hashed password
            
        Returns:
            User: New admin user instance
        """
        return cls.build(
            email=email,
            username=username,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=True
        )