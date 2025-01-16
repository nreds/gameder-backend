from sqlalchemy import Column, Text
from pydantic import BaseModel

from database import Base

__all__ = [
    "GameData",
    "GameDataBase"
]

class GameData(Base):
    __tablename__ = "game_data"

    name = Column(Text, primary_key=True)
    img = Column(Text)

class GameDataBase(BaseModel):
    name: str
    img: str


