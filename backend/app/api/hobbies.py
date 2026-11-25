"""Hobby endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.models import Hobby
from app.schemas.schemas import HobbyCreate, HobbyUpdate, HobbyResponse

router = APIRouter(tags=["hobbies"])


@router.get("", response_model=list[HobbyResponse])
async def list_hobbies(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List current user's hobbies."""
    hobbies = db.query(Hobby).filter(
        Hobby.user_id == UUID(current_user["id"])
    ).offset(skip).limit(limit).all()
    return hobbies


@router.post("", response_model=HobbyResponse, status_code=status.HTTP_201_CREATED)
async def create_hobby(
    hobby: HobbyCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new hobby."""
    db_hobby = Hobby(
        user_id=UUID(current_user["id"]),
        name=hobby.name,
        description=hobby.description,
        category=hobby.category
    )
    db.add(db_hobby)
    db.commit()
    db.refresh(db_hobby)
    return db_hobby


@router.put("/{hobby_id}", response_model=HobbyResponse)
async def update_hobby(
    hobby_id: UUID,
    hobby_update: HobbyUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a hobby."""
    hobby = db.query(Hobby).filter(Hobby.id == hobby_id).first()
    if not hobby:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hobby not found")
    
    # Ownership check
    if hobby.user_id != UUID(current_user["id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    if hobby_update.name is not None:
        hobby.name = hobby_update.name
    if hobby_update.description is not None:
        hobby.description = hobby_update.description
    if hobby_update.category is not None:
        hobby.category = hobby_update.category
    
    db.commit()
    db.refresh(hobby)
    return hobby


@router.delete("/{hobby_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hobby(
    hobby_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a hobby."""
    hobby = db.query(Hobby).filter(Hobby.id == hobby_id).first()
    if not hobby:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hobby not found")
    
    # Ownership check
    if hobby.user_id != UUID(current_user["id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    db.delete(hobby)
    db.commit()
