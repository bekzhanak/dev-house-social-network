from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CreateUserRequest(BaseModel):
    name: str
    surname: str
    username: str
    date_of_birth: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ProfileResponse(BaseModel):
    id: int
    name: str
    surname: str
    date_of_birth: str
    created_at: datetime
    updated_at: datetime
    is_verified: bool
    last_login: Optional[datetime]
    is_active: bool
    user_id: int

    class Config:
        orm_mode = True

class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    date_of_birth: Optional[str] = None
    is_active: Optional[bool] = None


class CreatePostRequest(BaseModel):
    title: str
    text: str