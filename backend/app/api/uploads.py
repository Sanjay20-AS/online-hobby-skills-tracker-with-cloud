"""Upload endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.models import Upload, Hobby
from app.schemas.schemas import UploadResponse

router = APIRouter(tags=["uploads"])


@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    hobby_id: UUID,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a file for a hobby."""
    # Verify hobby exists and belongs to user
    hobby = db.query(Hobby).filter(Hobby.id == hobby_id).first()
    if not hobby:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hobby not found")
    
    if hobby.user_id != UUID(current_user["id"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    # In a real implementation, would upload to Supabase Storage
    # For now, just store metadata
    file_size = len(await file.read())
    await file.seek(0)
    
    # Create storage path
    file_path = f"uploads/{current_user['id']}/{hobby_id}/{file.filename}"
    
    db_upload = Upload(
        user_id=UUID(current_user["id"]),
        hobby_id=hobby_id,
        file_path=file_path,
        original_filename=file.filename,
        file_size=file_size
    )
    db.add(db_upload)
    db.commit()
    db.refresh(db_upload)
    return db_upload
