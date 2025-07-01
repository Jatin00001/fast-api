from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.sql import Base
from datetime import datetime

class HomePageDestinations(Base):
    __tablename__ = "home_page_destinations"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=False, index=True)
    city = Column(String, nullable=False)
    order = Column(Integer, unique=True, index=True, nullable=False)
    image = Column(Integer, ForeignKey("files.id"), nullable=True)
    image_url = Column(String, nullable=True)
    
    @classmethod
    def build(cls, **kwargs):
        """Build a new instance with validated fields"""
        allowed_fields = {"city", "order", "is_active", "image", "image_url"}
        filtered_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
        return cls(**filtered_data)