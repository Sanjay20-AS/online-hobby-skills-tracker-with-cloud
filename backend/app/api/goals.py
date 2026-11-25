"""Goal endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.models import Goal, Hobby, Milestone
from app.schemas.schemas import GoalCreate, GoalUpdate, GoalResponse

router = APIRouter(tags=["goals"])


@router.get("", response_model=list[GoalResponse])
async def list_goals(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List current user's goals."""
    goals = db.query(Goal).filter(
        Goal.user_id == UUID(current_user["id"])
    ).offset(skip).limit(limit).all()
    return goals


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal: GoalCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new goal."""
    # Verify hobby exists and belongs to user
    hobby = db.query(Hobby).filter(Hobby.id == goal.hobby_id).first()
    if not hobby:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hobby not found")
    
    if hobby.user_id != UUID(current_user["id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    db_goal = Goal(
        user_id=UUID(current_user["id"]),
        hobby_id=goal.hobby_id,
        title=goal.title,
        description=goal.description,
        target_hours=goal.target_hours
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: UUID,
    goal_update: GoalUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update goal status. When status changes to 'completed', auto-unlock milestones."""
    db_goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not db_goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    
    if db_goal.user_id != UUID(current_user["id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    # Update status if provided
    if goal_update.status:
        valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        if goal_update.status not in valid_statuses:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        db_goal.status = goal_update.status
        
        # Auto-unlock milestones when goal is completed
        if goal_update.status == 'completed':
            milestones = db.query(Milestone).filter(
                Milestone.goal_id == goal_id,
                Milestone.achieved_at.is_(None)  # Only unlock unachieved milestones
            ).all()
            for milestone in milestones:
                milestone.achieved_at = datetime.utcnow()
    
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal
