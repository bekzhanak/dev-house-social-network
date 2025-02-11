from fastapi import APIRouter, HTTPException
from starlette import status
from dependencies import *
from models import Users, Profiles, Posts
from schemas import *
from datetime import datetime

router = APIRouter(
    prefix='/posts',
    tags=['posts']
)


@router.post("/create_post", status_code=status.HTTP_201_CREATED)
async def create_post(current_user: user_dependency, db: db_dependency, create_post_request: CreatePostRequest):
    create_post_request = Posts(
        title=create_post_request.title,
        text=create_post_request.text,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        user_id=current_user['id']
    )
    db.add(create_post_request)
    db.commit()
