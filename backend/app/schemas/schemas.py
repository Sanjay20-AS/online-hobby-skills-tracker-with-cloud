"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


# Profile schemas
class ProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class ProfileResponse(BaseModel):
    id: UUID
    username: str
    display_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    visibility: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Hobby schemas
class HobbyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None


class HobbyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


class HobbyResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    description: Optional[str]
    category: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Skill schemas
class SkillCreate(BaseModel):
    hobby_id: UUID
    name: str
    proficiency_level: Optional[str] = "beginner"


class SkillUpdate(BaseModel):
    hobby_id: UUID
    name: str
    proficiency_level: str = "beginner"


class SkillResponse(BaseModel):
    id: UUID
    user_id: UUID
    hobby_id: UUID
    name: str
    proficiency_level: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Goal schemas
class GoalCreate(BaseModel):
    hobby_id: UUID
    title: str
    description: Optional[str] = None
    target_hours: Optional[int] = None


class GoalUpdate(BaseModel):
    status: Optional[str] = None


class GoalResponse(BaseModel):
    id: UUID
    user_id: UUID
    hobby_id: UUID
    title: str
    description: Optional[str]
    target_hours: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Practice session schemas
class PracticeSessionCreate(BaseModel):
    skill_id: UUID
    duration_minutes: int


class PracticeSessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    hobby_id: UUID
    skill_id: Optional[UUID]
    duration_minutes: int
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Milestone schemas
class MilestoneCreate(BaseModel):
    goal_id: UUID
    title: str
    description: Optional[str] = None


class MilestoneResponse(BaseModel):
    id: UUID
    goal_id: UUID
    title: str
    description: Optional[str]
    achieved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Upload schemas
class UploadCreate(BaseModel):
    hobby_id: UUID
    file_path: str
    original_filename: str
    file_size: int


class UploadResponse(BaseModel):
    id: UUID
    user_id: UUID
    hobby_id: UUID
    file_path: str
    original_filename: str
    file_size: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Post schemas
class PostCreate(BaseModel):
    hobby_id: UUID
    title: str
    content: str
    visibility: Optional[str] = "private"


class PostResponse(BaseModel):
    id: UUID
    user_id: UUID
    hobby_id: UUID
    title: str
    content: str
    visibility: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Comment schemas
class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: UUID
    post_id: UUID
    user_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Feed schemas
class FeedPostResponse(BaseModel):
    id: UUID
    user_id: UUID
    hobby_id: UUID
    title: str
    content: str
    visibility: str
    username: str
    created_at: datetime
    like_count: int
    comment_count: int

    class Config:
        from_attributes = True


# Analytics schemas
class AnalyticsOverview(BaseModel):
    total_hobbies: int
    total_skills: int
    total_practice_hours: float
    total_goals: int
    completed_milestones: int
    public_posts: int
