from geoalchemy2.types import Geometry
from sqlalchemy.future import select
from typing import List, Optional

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime
from app.db.sql import Base
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql import func


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    showon_destmenu = Column(Boolean, default=False)
    location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=True)
    country_code = Column(String)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # ✅ Build Method
    @classmethod
    def build(
        cls,
        name: str,
        country_code: str,
        slug: Optional[str] = None,
        location: Optional[str] = None,
        image_id: Optional[int] = None,
        image_url: Optional[str] = None,
        showon_destmenu: bool = False
    ) -> "Country":

        # Auto-generate slug if not provided
        if not slug:
            import re
            slug = name.lower().strip()
            slug = re.sub(r'[\s_]+', '-', slug)
            slug = re.sub(r'-+', '-', slug)
            slug = slug.strip('-')
        
        # Normalize country code to uppercase
        country_code = country_code.upper() if country_code else country_code
        
        return cls(
            name=name,
            slug=slug,
            country_code=country_code,
            location=location,
            image_id=image_id,
            image_url=image_url,
            showon_destmenu=showon_destmenu
        )

   

    # ✅ Existing Database Methods
    @classmethod
    async def get_by_code(cls, db: AsyncSession, code: str):
        result = await db.execute(select(cls).where(cls.country_code == code))
        return result.scalar_one_or_none()

    @classmethod
    async def get(cls, db: AsyncSession, id: int):
        result = await db.execute(select(cls).where(cls.id == id))
        return result.scalar_one_or_none()

    @classmethod
    async def get_multi(cls, db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(cls).offset(skip).limit(limit))
        return result.scalars().all()

    @classmethod
    async def create(cls, db: AsyncSession, obj_in):
        if hasattr(obj_in, 'dict'):
            db_obj = cls(**obj_in.dict())
        else:
            db_obj = cls(**obj_in.__dict__)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @classmethod
    async def update(cls, db: AsyncSession, db_obj, obj_in):
        if hasattr(obj_in, 'dict'):
            obj_data = obj_in.dict(exclude_unset=True)
        else:
            obj_data = {k: v for k, v in obj_in.__dict__.items() if v is not None}
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @classmethod
    async def remove(cls, db: AsyncSession, id: int):
        obj = await cls.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj