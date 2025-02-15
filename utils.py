import os
from datetime import timezone, timedelta
from typing import Annotated

from dotenv import load_dotenv
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from starlette import status

from models import *

SECRET_KEY = os.getenv("JWT_KEY")
ALGORITHM = os.getenv("ALGORITHM_TYPE")
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


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
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/login')
token_dependency = Annotated[str, Depends(oauth2_bearer)]


async def get_current_user(token: token_dependency):
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
