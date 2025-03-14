from fastapi import APIRouter, BackgroundTasks
import random
from pathlib import Path
from dependencies import *
from fastapi.security import OAuth2PasswordRequestForm
from schemas import *
from utils import *
from routers.email_verification import send_email
from models import *

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest, background_tasks: BackgroundTasks):
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
        is_verified=False,
        last_login=None,
        is_active=True,
        user_id=create_user_model.id
    )

    verification_code = str(random.randint(1000, 9999))

    create_email = Emails(
        created_at=datetime.utcnow(),
        user_id=create_user_model.id,
        attempts=0,
        verification_code=verification_code
    )

    await send_email(background_tasks, recipient=create_user_request.email, body=verification_code)

    db.add(create_profile_model)
    db.commit()


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not authenticate user')

    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=180))
    return {'access_token': token, 'token_type': 'bearer'}


@router.post("/verify")
async def verify_user(current_user: user_dependency, db: db_dependency, user_code: int = Path(gt=0)):
    user_profile = db.query(Profiles).filter(Profiles.user_id == current_user['id']).first()
    if user_profile.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already verified")
    email = db.query(Emails).filter(Emails.user_id == current_user['id']).first()

    if not email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active verification code")
    if email.verification_code != user_code:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Wrong verification code")

    user_profile.is_verified = True
    user_profile.updated_at = datetime.utcnow()
    db.delete(email)
    db.commit()
    db.refresh(user_profile)
    return user_profile


async def is_verified(current_user: user_dependency, db: db_dependency):
    user_profile = db.query(Profiles).filter(Profiles.user_id == current_user['id']).first()
    if not user_profile.is_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not verified")
    return user_profile
