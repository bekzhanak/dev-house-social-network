from pathlib import Path

from fastapi import APIRouter, HTTPException
from starlette import status
from dependencies import *
from models import Users, Profiles, Posts, Comments
from schemas import *
from datetime import datetime

router = APIRouter(
    prefix='/comments',
    tags=['comments']
)


@router.post("/{post_id}", status_code=status.HTTP_201_CREATED)
async def create_comment(current_user: user_dependency, db: db_dependency, create_comment_request: CreateCommentRequest,
                         post_id: int = Path(gt=0)):
    current_post = db.query(Posts).filter(Posts.id == post_id).first()
    if not current_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    new_comment = Comments(
        text=create_comment_request.text,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        user_id=current_user['id'],
        post_id=current_post.id
    )
    db.add(new_comment)
    db.commit()


@router.get("/post/{post_id}")
async def get_comments_from_post(current_user: user_dependency, db: db_dependency, post_id: int = Path(gt=0)):
    request_post = db.query(Posts).filter(Posts.id == post_id).first()
    comments_from_post = db.query(Comments).filter(Comments.post_id == post_id).all()
    if not request_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if not comments_from_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comments to that post not found")
    return comments_from_post


@router.get("/my")
async def get_my_comments(current_user: user_dependency, db: db_dependency):
    user_comments = db.query(Comments).filter(Comments.user_id == current_user['id']).all()
    if not user_comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comments to that post not found")
    return user_comments


@router.put("/{comment_id}")
async def update_comment(update_data: UpdateCommentRequest, current_user: user_dependency, db: db_dependency,
                         comment_id: int = Path(gt=0)):
    user_comment = db.query(Comments).filter(Comments.user_id == current_user['id'], Comments.id == comment_id).first()
    if not user_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if update_data.text is not None:
        user_comment.text = update_data.text

    user_comment.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(user_comment)
    return user_comment


@router.delete("/{comment_id}")
async def delete_comment(current_user: user_dependency, db: db_dependency, comment_id: int = Path(gt=0)):
    user_comment = db.query(Comments).filter(Comments.user_id == current_user['id'], Comments.id == comment_id).first()
    if not user_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    db.delete(user_comment)
    db.commit()
    return {"detail": "Comment deleted successfully"}
