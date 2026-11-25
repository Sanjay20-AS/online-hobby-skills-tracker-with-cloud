"""Profile endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.models import Profile
from app.schemas.schemas import ProfileResponse, ProfileUpdate

router = APIRouter(tags=["profiles"])


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's profile."""
    profile = db.query(Profile).filter(Profile.id == UUID(current_user["id"])).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_update: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the current user's profile."""
    profile = db.query(Profile).filter(Profile.id == UUID(current_user["id"])).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    
    if profile_update.display_name is not None:
        profile.display_name = profile_update.display_name
    if profile_update.bio is not None:
        profile.bio = profile_update.bio
    if profile_update.avatar_url is not None:
        profile.avatar_url = profile_update.avatar_url
    
    db.commit()
    db.refresh(profile)
    return profile
