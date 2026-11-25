"""Tests for authentication."""

import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from app.main import app

client = TestClient(app)


def test_unauthorized_request():
    """Test that unauthorized requests are rejected."""
    response = client.get("/api/v1/profiles/me")
    assert response.status_code == 403


def test_invalid_token():
    """Test that invalid tokens are rejected."""
    response = client.get(
        "/api/v1/profiles/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_endpoints_require_auth():
    """Test that protected endpoints require authentication."""
    protected_endpoints = [
        "/api/v1/profiles/me",
        "/api/v1/hobbies",
        "/api/v1/skills",
        "/api/v1/goals",
        "/api/v1/sessions",
        "/api/v1/analytics/overview",
    ]
    
    for endpoint in protected_endpoints:
        response = client.get(endpoint)
        assert response.status_code in [401, 403], f"Endpoint {endpoint} should require auth"
