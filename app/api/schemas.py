from pydantic import BaseModel
from typing import Optional


class UserSchema(BaseModel):
    id: int
    yandex_id: str
    login: str
    is_superuser: Optional[bool] = False

    class Config:
        orm_mode = True


class AudioFileSchema(BaseModel):
    id: int
    display_name: str
    file_path: str

    class Config:
        orm_mode = True