"""Practice session endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.models import PracticeSession, Skill
from app.schemas.schemas import PracticeSessionCreate, PracticeSessionResponse

router = APIRouter(tags=["sessions"])


@router.get("", response_model=list[PracticeSessionResponse])
async def list_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List current user's practice sessions."""
    sessions = db.query(PracticeSession).filter(
        PracticeSession.user_id == UUID(current_user["id"])
    ).offset(skip).limit(limit).all()
    return sessions


@router.post("", response_model=PracticeSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: PracticeSessionCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new practice session."""
    # Verify skill exists and belongs to user
    skill = db.query(Skill).filter(Skill.id == session_data.skill_id).first()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    
    if skill.user_id != UUID(current_user["id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    # Verify hobby exists (from the skill's hobby_id)
    if not skill.hobby_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Skill must be associated with a hobby")
    
    db_session = PracticeSession(
        user_id=UUID(current_user["id"]),
        hobby_id=skill.hobby_id,
        skill_id=session_data.skill_id,
        duration_minutes=session_data.duration_minutes,
        notes=getattr(session_data, 'notes', None)
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session
