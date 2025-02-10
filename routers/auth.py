from typing import Annotated, Optional
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import Sessionlocal
from models import Users, Profiles
from passlib.context import  CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError

load_dotenv()
SECRET_KEY = os.getenv("JWT_KEY")
ALGORITHM = os.getenv("ALGORITHM_TYPE")

router = APIRouter(
    prefix = '/auth',
    tags = ['auth']
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
    name: str
    surname: str
    username: str
    date_of_birth: str
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type:str


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()


db_dependeny = Annotated[Session, Depends(get_db)]


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
        orm_mode = True  # Allows returning ORM objects directly


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    date_of_birth: Optional[str] = None
    is_active: Optional[bool] = None


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    user_profile = db.query(Profiles).filter(Profiles.user_id == user.id).first()
    user_profile.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user_profile)
    return user



def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id' : user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not find such user')
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                        detail='Could not access JWT')

user_dependency = Annotated[dict, Depends(get_current_user)]
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependeny, create_user_request: CreateUserRequest):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        role="user",
        hashed_password=bcrypt_context.hash(create_user_request.password),
    )
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    create_profile_model = Profiles(
        name=create_user_request.name,
        surname=create_user_request.surname,
        date_of_birth=create_user_request.date_of_birth,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_verified=True,
        last_login=None,
        is_active=True,
        user_id=create_user_model.id
    )

    db.add(create_profile_model)
    db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependeny):

    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not authenticate user')

    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=180))
    return {'access_token': token, 'token_type':'bearer'}

@router.get("/get-profile", response_model=ProfileResponse)
async def get_profile(current_user: user_dependency, db: db_dependeny):
    user_profile = db.query(Profiles).filter(Profiles.user_id == current_user['id']).first()
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return user_profile


@router.put("/update-profile", response_model=ProfileResponse)
async def update_profile(update_data: UpdateProfileRequest, current_user: user_dependency, db: db_dependeny):

    user_profile = db.query(Profiles).filter(Profiles.user_id == current_user['id']).first()
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    if update_data.name is not None:
        user_profile.name = update_data.name
    if update_data.surname is not None:
        user_profile.surname = update_data.surname
    if update_data.date_of_birth is not None:
        user_profile.date_of_birth = update_data.date_of_birth
    if update_data.is_active is not None:
        user_profile.is_active = update_data.is_active

    user_profile.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(user_profile)
    return user_profile

@router.delete("/delete-profile")
async def delete_profile(current_user: user_dependency,db: db_dependeny):

    user_profile = db.query(Profiles).filter(Profiles.user_id == current_user['id']).first()
    user_user = db.query(Users).filter(Users.id == current_user['id']).first()
    if not user_profile or not user_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile or user not found")

    db.delete(user_profile)
    db.delete(user_user)
    db.commit()
    return {"detail": "Profile deleted successfully"}