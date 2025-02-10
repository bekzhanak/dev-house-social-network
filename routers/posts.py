from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from database import Sessionlocal
from models import Users, Profiles, Posts
from passlib.context import  CryptContext

from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from datetime import timedelta, datetime, timezone

from .auth import get_current_user

router = APIRouter(
    prefix = '/posts',
    tags=['posts']
)


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()

db_dependeny = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class CreatePostRequest(BaseModel):
    title: str
    text: str

@router.post("/create_post", status_code=status.HTTP_201_CREATED)
async def create_post(current_user: user_dependency, db: db_dependeny, create_post_request: CreatePostRequest):
    create_post_request = Posts(
        title=create_post_request.title,
        text=create_post_request.text,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        user_id=current_user['id']
    )
    db.add(create_post_request)
    db.commit()