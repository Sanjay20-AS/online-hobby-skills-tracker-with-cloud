"""Pytest configuration and fixtures."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4
import jwt

from app.core.config import settings
from app.core.database import get_db
from app.models.models import Base, Profile
from app.main import app


# Create test database
engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def test_user():
    """Create a test user and return credentials."""
    user_id = str(uuid4())
    # Create JWT token
    token = jwt.encode(
        {"sub": user_id, "email": "test@example.com"},
        "secret",
        algorithm="HS256"
    )
    return {"id": user_id, "token": token}


@pytest.fixture
def db_session():
    """Create a test database session."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
