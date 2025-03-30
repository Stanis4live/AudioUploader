from jose import jwt, JWTError
from datetime import datetime, timedelta, UTC
from decouple import config
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Header, Depends, HTTPException

from app.services.database.models import User
from app.services.database.db_config import get_async_session

SECRET_KEY = config("SECRET_KEY")

def create_internal_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(UTC) + timedelta(days=30),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


async def get_or_create_user(session: AsyncSession, user_info: dict) -> User:
    result = await session.execute(select(User).where(User.yandex_id == user_info.get("id")))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            yandex_id=user_info.get("id"),
            login=user_info.get("login"),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        user.internal_token = create_internal_token(user.id)
        await session.commit()

    return user


async def get_current_user(Authorization: str = Header(...), session: AsyncSession = Depends(get_async_session)) -> User:
    token = Authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Invalid token")

    return user