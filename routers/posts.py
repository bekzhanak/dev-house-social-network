from pathlib import Path

from fastapi import APIRouter, HTTPException
from starlette import status
from dependencies import *
from models import *
from schemas import *
from datetime import datetime

router = APIRouter(
    prefix='/posts',
    tags=['posts']
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(current_user: user_dependency, db: db_dependency, create_post_request: CreatePostRequest):
    new_post = Posts(
        title=create_post_request.title,
        text=create_post_request.text,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        user_id=current_user['id']
    )
    db.add(new_post)
    db.commit()


@router.get("/lenta")
async def get_all_post(current_user: user_dependency, db: db_dependency):
    all_posts = db.query(Posts).all()
    if not all_posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no posts yes!")
    return all_posts


@router.get("/post_by_user/{user_id}")
async def get_posts_by_user(current_user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):
    user_posts = db.query(Posts).filter(Posts.user_id == user_id).all()
    if not user_posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return user_posts


@router.get("/{post_id}")
async def get_post(current_user: user_dependency, db: db_dependency, post_id: int = Path(gt=0)):
    user_post = db.query(Posts).filter(Posts.id == post_id).first()
    if not user_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return user_post



@router.put("/{post_id}")
async def update_post(update_data: UpdatePostRequest, current_user: user_dependency, db: db_dependency,
                      post_id: int = Path(gt=0)):
    user_post = db.query(Posts).filter(Posts.user_id == current_user['id'], Posts.id == post_id).first()
    if not user_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if update_data.title is not None:
        user_post.title = update_data.title
    if update_data.text is not None:
        user_post.text = update_data.text

    user_post.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(user_post)
    return user_post


@router.delete("/{post_id}")
async def delete_post(current_user: user_dependency, db: db_dependency, post_id: int = Path(gt=0)):
    user_post = db.query(Posts).filter(Posts.user_id == current_user['id'], Posts.id == post_id).first()
    if not user_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    db.delete(user_post)
    db.commit()
    return {"detail": "Post deleted successfully"}
