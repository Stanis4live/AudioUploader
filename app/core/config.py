from decouple import config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth_router, audio_router


main_app = FastAPI(
    title="Uploader App",
    description="Uploader Service",
    version="0.1",
)

main_app.add_middleware(
    CORSMiddleware,
    allow_origins=config("ALLOWED_ORIGINS").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

main_app.include_router(auth_router)
main_app.include_router(audio_router)