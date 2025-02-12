from fastapi import APIRouter, HTTPException
from starlette import status
from dependencies import *
from fastapi.security import OAuth2PasswordRequestForm
from schemas import *
from utils import *

router = APIRouter(
    prefix='/profile',
    tags=['profile']
)

@router.get("/me", response_model=ProfileResponse)
async def get_profile(current_user: user_dependency, db: db_dependency):
    user_profile = db.query(Profiles).filter(Profiles.user_id == current_user['id']).first()
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return user_profile


@router.put("/me", response_model=ProfileResponse)
async def update_profile(update_data: UpdateProfileRequest, current_user: user_dependency, db: db_dependency):

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


@router.delete("/me")
async def delete_profile(current_user: user_dependency, db: db_dependency):
    user_profile = db.query(Profiles).filter(Profiles.user_id == current_user['id']).first()
    user = db.query(Users).filter(Users.id == current_user['id']).first()
    if not user_profile or not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile or user not found")

    db.delete(user_profile)
    db.delete(user)
    db.commit()
    return {"detail": "Profile deleted successfully"}