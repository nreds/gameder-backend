from sqlalchemy import Column, ForeignKey, Text, Integer
from sqlalchemy.orm import mapped_column
from pydantic import BaseModel

from database import Base

__all__ = [
    "AccountData",
    "AccountDataBase",
    "AccountRequest",
    "UserPrefs",
    "UserPrefsBase"
]

class AccountData(Base):
    __tablename__ = "credentials"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Text)
    username = Column(Text, unique=True)
    email = Column(Text, unique=True)

class AccountDataBase(BaseModel):
    uid: str
    username: str
    email: str


class AccountRequest(BaseModel):
    uid: str | None = None
    username: str | None = None
    email: str | None = None

    def dict(self):
        data = {}
        for field in self.model_dump():
            if self.__dict__[field] is not None:
                data[field] = self.__dict__[field]

        return data

class UserPrefs(Base):
    __tablename__ = "user_prefs"

    user_id = mapped_column(ForeignKey("credentials.user_id"), primary_key=True)
    username = mapped_column(ForeignKey("credentials.username"), unique=True)
    profile = Column(Text, default="private")

class UserPrefsBase(BaseModel):
    user_id: int
    username: str
    profile: str = "private"