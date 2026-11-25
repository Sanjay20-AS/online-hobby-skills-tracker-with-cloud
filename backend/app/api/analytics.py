"""Analytics endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.models import Hobby, Skill, Goal, Milestone, PracticeSession, Post
from app.schemas.schemas import AnalyticsOverview

router = APIRouter(tags=["analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics overview for current user."""
    user_id = UUID(current_user["id"])
    
    total_hobbies = db.query(func.count(Hobby.id)).filter(Hobby.user_id == user_id).scalar() or 0
    total_skills = db.query(func.count(Skill.id)).filter(Skill.user_id == user_id).scalar() or 0
    
    # Total practice hours
    total_practice_minutes = db.query(func.sum(PracticeSession.duration_minutes)).filter(
        PracticeSession.user_id == user_id
    ).scalar() or 0
    total_practice_hours = total_practice_minutes / 60
    
    total_goals = db.query(func.count(Goal.id)).filter(Goal.user_id == user_id).scalar() or 0
    
    completed_milestones = db.query(func.count(Milestone.id)).filter(
        Milestone.achieved_at.isnot(None)
    ).scalar() or 0
    
    public_posts = db.query(func.count(Post.id)).filter(
        Post.user_id == user_id,
        Post.visibility == "public"
    ).scalar() or 0
    
    return AnalyticsOverview(
        total_hobbies=total_hobbies,
        total_skills=total_skills,
        total_practice_hours=total_practice_hours,
        total_goals=total_goals,
        completed_milestones=completed_milestones,
        public_posts=public_posts
    )
