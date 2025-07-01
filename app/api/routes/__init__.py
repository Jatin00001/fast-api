from fastapi import APIRouter

from app.api.routes import (
    auth,
    city,
    country,
    home_page_destinations,
    image,
    storage,
    users,
)

router = APIRouter()

# Authentication and User Management
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])

# Location Management
router.include_router(city.router, prefix="/cities", tags=["Cities"])
router.include_router(country.router, prefix="/countries", tags=["Countries"])

# Content Management
router.include_router(image.router, prefix="/images", tags=["Images"])
router.include_router(storage.router, prefix="/storage", tags=["Storage"])
router.include_router(
    home_page_destinations.router,
    prefix="/home-destinations",
    tags=["Home Destinations"]
)
