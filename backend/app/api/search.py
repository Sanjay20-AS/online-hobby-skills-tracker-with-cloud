"""Search endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.models import Hobby, Post, Profile, Skill

router = APIRouter(tags=["search"])


@router.get("")
async def search(
    q: str = Query("", min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search hobbies, skills, and public posts."""
    results = {
        "hobbies": [],
        "skills": [],
        "posts": [],
        "profiles": []
    }
    
    if q:
        # Search hobbies (user's own only)
        hobbies = db.query(Hobby).filter(
            Hobby.user_id == UUID(current_user["id"]),
            Hobby.name.ilike(f"%{q}%")
        ).offset(skip).limit(limit).all()
        results["hobbies"] = [
            {
                "id": str(h.id),
                "name": h.name,
                "description": h.description
            } for h in hobbies
        ]
        
        # Search skills (user's own only)
        skills = db.query(Skill).filter(
            Skill.user_id == UUID(current_user["id"]),
            Skill.name.ilike(f"%{q}%")
        ).offset(skip).limit(limit).all()
        results["skills"] = [
            {
                "id": str(s.id),
                "name": s.name,
                "proficiency_level": s.proficiency_level,
                "description": None
            } for s in skills
        ]
        
        # Search public posts
        posts = db.query(Post).filter(
            Post.visibility == "public",
            Post.title.ilike(f"%{q}%")
        ).offset(skip).limit(limit).all()
        results["posts"] = [
            {
                "id": str(p.id),
                "title": p.title,
                "content": p.content[:100]
            } for p in posts
        ]
        
        # Search profiles (public only)
        profiles = db.query(Profile).filter(
            Profile.visibility == "public",
            Profile.username.ilike(f"%{q}%")
        ).offset(skip).limit(limit).all()
        results["profiles"] = [
            {
                "id": str(p.id),
                "username": p.username,
                "display_name": p.display_name
            } for p in profiles
        ]
    
    return results
