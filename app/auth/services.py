from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User
from .security import get_password_hash
from app.schemas import UserBase, UserCreate


async def get_user_by_email(session: AsyncSession, email: str):
    smtp = select(User).where(User.email == email)
    result = await session.execute(smtp)
    user = result.scalars().first()
    return user


async def create_user(session: AsyncSession, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        hashed_password=hashed_password
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user
