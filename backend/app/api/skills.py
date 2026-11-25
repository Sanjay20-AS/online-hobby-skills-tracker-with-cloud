"""Skill endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.models import Skill, Hobby, PracticeSession
from app.schemas.schemas import SkillCreate, SkillUpdate, SkillResponse

router = APIRouter(tags=["skills"])


@router.get("", response_model=list[SkillResponse])
async def list_skills(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List current user's skills."""
    skills = db.query(Skill).filter(
        Skill.user_id == UUID(current_user["id"])
    ).offset(skip).limit(limit).all()
    return skills


@router.post("", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill: SkillCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new skill."""
    # Verify hobby exists and belongs to user
    hobby = db.query(Hobby).filter(Hobby.id == skill.hobby_id).first()
    if not hobby:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hobby not found")
    
    if hobby.user_id != UUID(current_user["id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    db_skill = Skill(
        user_id=UUID(current_user["id"]),
        hobby_id=skill.hobby_id,
        name=skill.name,
        proficiency_level=skill.proficiency_level
    )
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill


@router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: UUID,
    skill_update: SkillUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a skill."""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    
    # Authorization check
    if skill.user_id != UUID(current_user["id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    # Verify new hobby exists and belongs to user
    if skill_update.hobby_id != skill.hobby_id:
        hobby = db.query(Hobby).filter(Hobby.id == skill_update.hobby_id).first()
        if not hobby:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hobby not found")
        
        if hobby.user_id != UUID(current_user["id"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    skill.name = skill_update.name
    skill.hobby_id = skill_update.hobby_id
    skill.proficiency_level = skill_update.proficiency_level
    
    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a skill."""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    
    # Authorization check
    if skill.user_id != UUID(current_user["id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    # Check for dependent practice sessions
    dependent_sessions = db.query(PracticeSession).filter(
        PracticeSession.skill_id == skill_id
    ).count()
    
    if dependent_sessions > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete skill with {dependent_sessions} practice session(s). Please delete the sessions first."
        )
    
    db.delete(skill)
    db.commit()
