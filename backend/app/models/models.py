"""SQLAlchemy ORM models matching the deployed schema."""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Boolean, Enum, func, UUID as SQLUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    visibility = Column(String, default="private")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Hobby(Base):
    __tablename__ = "hobbies"
    
    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(SQLUUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(SQLUUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    hobby_id = Column(SQLUUID(as_uuid=True), ForeignKey("hobbies.id"), nullable=False)
    name = Column(String, nullable=False)
    proficiency_level = Column(String, default="beginner")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(SQLUUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    hobby_id = Column(SQLUUID(as_uuid=True), ForeignKey("hobbies.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    target_hours = Column(Integer, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PracticeSession(Base):
    __tablename__ = "practice_sessions"
    
    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(SQLUUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    hobby_id = Column(SQLUUID(as_uuid=True), ForeignKey("hobbies.id"), nullable=False)
    skill_id = Column(SQLUUID(as_uuid=True), ForeignKey("skills.id"), nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Milestone(Base):
    __tablename__ = "milestones"
    
    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(SQLUUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    goal_id = Column(SQLUUID(as_uuid=True), ForeignKey("goals.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    achieved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Upload(Base):
    __tablename__ = "uploads"
    
    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(SQLUUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    hobby_id = Column(SQLUUID(as_uuid=True), ForeignKey("hobbies.id"), nullable=False)
    file_path = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Post(Base):
    __tablename__ = "posts"
    
    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(SQLUUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    hobby_id = Column(SQLUUID(as_uuid=True), ForeignKey("hobbies.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    visibility = Column(String, default="private")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Like(Base):
    __tablename__ = "likes"
    
    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(SQLUUID(as_uuid=True), ForeignKey("posts.id"), nullable=False)
    user_id = Column(SQLUUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(SQLUUID(as_uuid=True), ForeignKey("posts.id"), nullable=False)
    user_id = Column(SQLUUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Follow(Base):
    __tablename__ = "follows"
    
    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    follower_id = Column(SQLUUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    following_id = Column(SQLUUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
