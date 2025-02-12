from fastapi import APIRouter, HTTPException
from starlette import status
from dependencies import *
from fastapi.security import OAuth2PasswordRequestForm
from schemas import *
from utils import *

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
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


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not authenticate user')

    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=180))
    return {'access_token': token, 'token_type': 'bearer'}



