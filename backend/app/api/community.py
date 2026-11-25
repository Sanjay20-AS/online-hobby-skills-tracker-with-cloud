"""Community/Feed endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.models import Post, Profile, Like, Comment
from app.schemas.schemas import PostCreate, PostResponse, CommentCreate, CommentResponse

router = APIRouter(tags=["community"])


@router.get("", response_model=list[dict])
@router.get("/feed", response_model=list[dict])
async def get_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feed of public posts from followed users."""
    # For simplicity, return public posts with like/comment counts
    posts = db.query(
        Post.id,
        Post.user_id,
        Post.hobby_id,
        Post.title,
        Post.content,
        Post.visibility,
        Post.created_at,
        Profile.username,
        func.count(Like.id).label("like_count"),
        func.count(Comment.id).label("comment_count")
    ).join(Profile, Post.user_id == Profile.id).outerjoin(Like, Post.id == Like.post_id).outerjoin(Comment, Post.id == Comment.post_id).filter(
        Post.visibility == "public"
    ).group_by(Post.id, Profile.username).offset(skip).limit(limit).all()
    
    return [
        {
            "id": p[0],
            "user_id": p[1],
            "hobby_id": p[2],
            "title": p[3],
            "content": p[4],
            "visibility": p[5],
            "created_at": p[6],
            "username": p[7],
            "like_count": p[8],
            "comment_count": p[9]
        }
        for p in posts
    ]


@router.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new post."""
    db_post = Post(
        user_id=UUID(current_user["id"]),
        hobby_id=post.hobby_id,
        title=post.title,
        content=post.content,
        visibility=post.visibility
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@router.post("/posts/{post_id}/likes", status_code=status.HTTP_201_CREATED)
async def like_post(
    post_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Like a post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    # Check if already liked
    existing_like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == UUID(current_user["id"])
    ).first()
    if existing_like:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already liked")
    
    db_like = Like(post_id=post_id, user_id=UUID(current_user["id"]))
    db.add(db_like)
    db.commit()
    return {"message": "Liked"}


@router.delete("/posts/{post_id}/likes", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_post(
    post_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unlike a post."""
    like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == UUID(current_user["id"])
    ).first()
    if not like:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Like not found")
    
    db.delete(like)
    db.commit()


@router.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: UUID,
    comment: CommentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a comment on a post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    db_comment = Comment(
        post_id=post_id,
        user_id=UUID(current_user["id"]),
        content=comment.content
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment
