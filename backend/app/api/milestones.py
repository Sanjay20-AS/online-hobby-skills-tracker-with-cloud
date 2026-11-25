"""Milestone endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.models import Milestone, Goal
from app.schemas.schemas import MilestoneCreate, MilestoneResponse

router = APIRouter(tags=["milestones"])


@router.get("", response_model=list[MilestoneResponse])
async def list_milestones(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List milestones for current user's goals."""
    # Get all milestones for current user's goals
    milestones = db.query(Milestone).join(Goal).filter(
        Goal.user_id == UUID(current_user["id"])
    ).offset(skip).limit(limit).all()
    return milestones


@router.post("", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
async def create_milestone(
    milestone: MilestoneCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new milestone."""
    # Verify goal exists and belongs to user
    goal = db.query(Goal).filter(Goal.id == milestone.goal_id).first()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    
    if goal.user_id != UUID(current_user["id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    db_milestone = Milestone(
        user_id=UUID(current_user["id"]),
        goal_id=milestone.goal_id,
        title=milestone.title,
        description=milestone.description
    )
    db.add(db_milestone)
    db.commit()
    db.refresh(db_milestone)
    return db_milestone
