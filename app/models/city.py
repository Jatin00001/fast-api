import enum
from geoalchemy2.types import Geometry
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, Enum
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func
from typing import Optional
from app.db.sql import Base

class RegionEnum(str, enum.Enum):
    """Enumeration for world regions"""
    asia = "asia"
    africa = "africa"
    europe = "europe"
    north_america = "north-america"
    south_america = "south-america"
    middle_east = "middle-east"
    oceania = "oceania"

class EnqAppTeamEnum(str, enum.Enum):
    """Enumeration for enquiry application teams"""
    london_uk = "london-uk"
    america = "america"
    europe = "europe"
    apac = "apac"
    mea = "mea"

class ManagerEnum(str, enum.Enum):
    """Enumeration for managers"""
    giles = "Giles"
    rachel = "Rachel"
    paridhi = "Paridhi"

class DestmenuCategoryEnum(str, enum.Enum):
    """Enumeration for destination menu categories"""
    london = "london"
    new_york = "new-york"
    paris = "paris"
    amsterdam = "amsterdam"
    berlin = "berlin"
    singapore = "singapore"
    san_francisco = "san-francisco"
    dublin = "dublin"
    tokyo = "tokyo"
    dubai = "dubai"
    hong_kong = "hong-kong"
    sydney = "sydney"
    worldwide = "worldwide"

class City(Base):
    """
    City model representing cities in the system
    """
    __tablename__ = "cities"

    # Primary key and timestamps
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Basic information
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=False, index=True)
    order = Column(Integer, default=9999, index=True)
    
    # Relationships
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=True)
    image_id = Column(Integer, ForeignKey('images.id'), nullable=True)
    image_url = Column(String, nullable=True)
    
    # Location data
    location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=True)
    

    @classmethod
    def build(
        cls,
        name: str,
        country_id: int,
        slug: Optional[str] = None,
        is_active: bool = True,
        image_id: Optional[int] = None,
        image_url: Optional[str] = None,
        order: int = 9999,
        location: Optional[str] = None,
    ) -> "City":
       
        # Auto-generate slug if not provided
        if not slug:
            import re
            slug = name.lower().strip()
            slug = re.sub(r'[\s_]+', '-', slug)
            slug = re.sub(r'-+', '-', slug)
            slug = slug.strip('-')
        
        return cls(
            name=name,
            slug=slug,
            country_id=country_id,
            is_active=is_active,
            image_id=image_id,
            image_url=image_url,
            order=order
        )

    # Optional fields (commented out for now, can be enabled as needed)
    # region = Column(Enum(RegionEnum, name="region_enum"), nullable=True, index=True)
    # destmenu_category = Column(Enum(DestmenuCategoryEnum, name="destmenu_enum"), nullable=True, index=True)
    # manager = Column(Enum(ManagerEnum, name="manager_enum"), nullable=True, index=True)
    # enq_app_team = Column(Enum(EnqAppTeamEnum, name="enq_team_enum"), nullable=True, index=True)
    # showon_destmenu = Column(Boolean, default=True)
    # vat_slabs = Column(JSONB, default=dict)
    # top_suburbs = Column(ARRAY(Integer))
    # all_suburbs = Column(ARRAY(Integer))
    # min_rent_amount = Column(Float)
    # min_rent_currency = Column(String(3), default='GBP')
    # all_exclusive_pages = Column(JSONB, default=dict)
    # top_five_props = Column(JSONB, default=list)
    # suppliers_serving = Column(JSONB, default=dict)
    # hidden_buildings = Column(JSONB, default=dict)
    # is_featured = Column(Boolean, default=True, index=True)
    # is_villa = Column(Boolean, default=False, index=True)
    # is_coliving = Column(Boolean, default=False, index=True)
    # is_hotel = Column(Boolean, default=False)
    # eco_grade_data = Column(JSONB, default=dict)
    # seo_data = Column(Text, default="")
    # seo_heading = Column(Text, default="")