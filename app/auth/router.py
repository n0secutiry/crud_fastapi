from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import verify_password, create_access_token
from app.auth.services import get_user_by_email, create_user
from app.celery_worker import send_welcome_email
from app.database import get_async_session
from app.schemas import UserCreate

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register")
async def register(
        new_user: UserCreate,
        session: AsyncSession = Depends(get_async_session),
):
    test_user = await get_user_by_email(session, new_user.email)
    if test_user is not None:
        raise HTTPException(
            status_code=400,
            detail="User already registered",
        )
    send_welcome_email.delay(new_user.email)
    return await create_user(session, new_user)


@router.post("/token")
async def token(
        session: AsyncSession = Depends(get_async_session),
        form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await get_user_by_email(session, form_data.username)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username",
        )
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password",
        )
    return create_access_token(
        {"sub": user.email},
    )