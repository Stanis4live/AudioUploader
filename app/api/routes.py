import httpx
import os
from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from decouple import config
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy.future import select
from fastapi.responses import RedirectResponse
from typing import Optional

from app.api.schemas import AudioFileSchema
from app.services.auth.auth import get_or_create_user, get_current_user, create_internal_token
from app.services.database.db_config import get_async_session
from app.services.database.models import User, AudioFile

auth_router = APIRouter(prefix="/auth/yandex")
audio_router = APIRouter(prefix="/audio")

YANDEX_CLIENT_ID = config("YANDEX_CLIENT_ID")
YANDEX_CLIENT_SECRET = config("YANDEX_CLIENT_SECRET")
YANDEX_REDIRECT_URI = config("YANDEX_REDIRECT_URI")
UPLOAD_DIR = config("UPLOAD_DIR")

os.makedirs(UPLOAD_DIR, exist_ok=True)


@auth_router.get("/login")
async def login():
    yandex_auth_url = (f"https://oauth.yandex.ru/authorize?"
                       f"response_type=code&client_id={YANDEX_CLIENT_ID}&redirect_uri={YANDEX_REDIRECT_URI}")
    return RedirectResponse (url=yandex_auth_url)


@auth_router.get("/callback")
async def callback(request: Request, session: AsyncSession = Depends(get_async_session)):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Code not provided")

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth.yandex.ru/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": YANDEX_CLIENT_ID,
                "client_secret": YANDEX_CLIENT_SECRET,
            }
        )

        token_response.raise_for_status()
        token_data = token_response.json()
        access_token = token_data.get("access_token")

        user_info_response = await client.get(
            "https://login.yandex.ru/info?",
            headers={"Authorization": f"OAuth {access_token}"},
        )
        user_info_response.raise_for_status()
        user_info_data = user_info_response.json()

    user = await get_or_create_user(session, user_info_data)

    return {"internal_token": user.internal_token}


@auth_router.post("/refresh_token")
async def refresh_token(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    new_token = create_internal_token(user.id)
    user.internal_token = new_token
    await session.commit()
    return {"internal_token": new_token}


@audio_router.post("/upload", response_model=AudioFileSchema)
async def upload_audio(
        file: UploadFile = File(...),
        display_name: Optional[str] = Form(None),
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    if not display_name:
        display_name = os.path.splitext(file.filename)[0]

    extension = os.path.splitext(file.filename)[-1]
    unique_name = f"{user.id}_{display_name}_{extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    audio = AudioFile(
        user_id=user.id,
        file_name=unique_name,
        display_name=display_name,
    )
    session.add(audio)
    await session.commit()
    await session.refresh(audio)

    return AudioFileSchema(id=audio.id, display_name=audio.display_name, file_path=file_path)


@audio_router.get("/")
async def list_audios(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(AudioFile).where(AudioFile.user_id == user.id))
    audio_files = result.scalars().all()
    response = [AudioFileSchema(id=audio_file.id, display_name=audio_file.display_name,
                                file_path=os.path.join(UPLOAD_DIR, audio_file.file_name)) for audio_file in audio_files]
    return response
