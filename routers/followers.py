from pathlib import Path
from fastapi import APIRouter, HTTPException
from starlette import status
from dependencies import *
from models import *
from schemas import *
from datetime import datetime

router = APIRouter(
    prefix='/followers',
    tags=['followers']
)

@router.post("/follow/{following_id}", status_code=status.HTTP_201_CREATED)
async def follow(current_user: user_dependency, db: db_dependency, following_id: int = Path(gt=0)):
    following_user = db.query(Users).filter(Users.id == following_id).first()
    if not following_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Such user not found")
    if following_id == current_user['id']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")

    exists_follow = db.query(Followers).filter(Followers.following_id == following_id, Followers.follower_id == current_user['id']).first()

    if exists_follow is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already follow them")

    new_follower = Followers(
        created_at=datetime.utcnow(),
        follower_id=current_user['id'],
        following_id=following_id
    )
    db.add(new_follower)
    db.commit()

@router.get("/{following_id}")
async def get_followers(current_user: user_dependency, db: db_dependency, following_id: int = Path(gt=0)):
    following_user = db.query(Users).filter(Users.id == following_id).first()
    if not following_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Such user not found")

    followers = db.query(Followers.follower_id).filter(Followers.following_id == following_id).all()
    all_followers = [follower_id[0] for follower_id in followers]
    return all_followers

@router.post("/unfollow/{following_id}")
async def unfollow(current_user: user_dependency, db: db_dependency, following_id: int = Path(gt=0)):
    following = db.query(Followers).filter(Followers.following_id == following_id, Followers.follower_id == current_user['id']).first()
    if not following:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You dont follow such user")

    db.delete(following)
    db.commit()
    return {"detail": "Following deleted successfully"}
