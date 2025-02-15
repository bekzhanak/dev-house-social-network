from pathlib import Path
from fastapi import APIRouter, HTTPException
from starlette import status
from dependencies import *
from models import *
from schemas import *
from datetime import datetime

router = APIRouter(
    prefix='/likes',
    tags=['likes']
)


@router.post("/{post_id}", status_code=status.HTTP_201_CREATED)
async def create_like(current_user: user_dependency, db: db_dependency, post_id: int = Path(gt=0)):
    current_post = db.query(Posts).filter(Posts.id == post_id).first()
    if not current_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    new_like = Likes(
        created_at=datetime.utcnow(),
        user_id=current_user['id'],
        post_id=current_post.id
    )
    db.add(new_like)
    db.commit()

@router.get("/{post_id}")
async def get_likes(current_user: user_dependency, db: db_dependency, post_id: int = Path(gt=0)):
    current_post = db.query(Posts).filter(Posts.id == post_id).first()
    if not current_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    likes_count = db.query(Likes).filter(Likes.post_id == post_id).count()
    return likes_count


@router.delete("/{post_id}")
async def delete_like(current_user: user_dependency, db: db_dependency, post_id: int = Path(gt=0)):
    user_like = db.query(Likes).filter(Likes.user_id == current_user['id'], Likes.post_id == post_id).first()
    if not user_like:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Like not found")

    db.delete(user_like)
    db.commit()
    return {"detail": "Like deleted successfully"}