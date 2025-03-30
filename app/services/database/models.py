from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, BigInteger, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    yandex_id = Column(String, unique=True, index=True, nullable=False)
    login = Column(String, unique=True, nullable=False)
    internal_token = Column(String, unique=True, nullable=False, default="")
    is_superuser = Column(Boolean, default=False)


class AudioFile(Base):
    __tablename__ = "audio_files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    file_name = Column(String, nullable=False)
    display_name = Column(String)

    user = relationship("User", backref="audio_files")