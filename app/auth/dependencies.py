import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import user

from .services import get_user_by_email
from app.config import SECRET_KEY, ALGORITHM
from app.database import get_async_session
from .security import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def authenticate_user(
        session: AsyncSession,
        email: str,
        password: str,
):
    registered_user = await get_user_by_email(session, email)
    if not registered_user:
        return False
    if not verify_password(password, registered_user.hashed_password):
        return False
    return registered_user



async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_async_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    user_by_email = await get_user_by_email(session, email)
    if user_by_email is None:
        raise credentials_exception
    return user_by_email



