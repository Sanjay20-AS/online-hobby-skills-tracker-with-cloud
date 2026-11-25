from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import profiles, hobbies, skills, goals, sessions, milestones, uploads, community, analytics, search

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url=f"{settings.api_v1_prefix}/docs",
    redoc_url=f"{settings.api_v1_prefix}/redoc",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with their respective prefixes
app.include_router(profiles.router, prefix=f"{settings.api_v1_prefix}/profiles")
app.include_router(hobbies.router, prefix=f"{settings.api_v1_prefix}/hobbies")
app.include_router(skills.router, prefix=f"{settings.api_v1_prefix}/skills")
app.include_router(goals.router, prefix=f"{settings.api_v1_prefix}/goals")
app.include_router(sessions.router, prefix=f"{settings.api_v1_prefix}/sessions")
app.include_router(milestones.router, prefix=f"{settings.api_v1_prefix}/milestones")
app.include_router(uploads.router, prefix=f"{settings.api_v1_prefix}/uploads")
# Community router: register at /api/v1 so /feed endpoint becomes /api/v1/feed
app.include_router(community.router, prefix=f"{settings.api_v1_prefix}")
app.include_router(analytics.router, prefix=f"{settings.api_v1_prefix}/analytics")
app.include_router(search.router, prefix=f"{settings.api_v1_prefix}/search")


@app.get("/health")
async def health_check():
    """Basic health check endpoint for startup verification."""
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}
