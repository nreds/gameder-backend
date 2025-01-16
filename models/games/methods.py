from .models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

__all__ = [
    "get_game_data",
    "insert_game_data"
]

async def get_game_data(name: str, session: AsyncSession) -> GameData:
    game = (await session.scalars(select(GameData).filter_by(name=name))).first()

    return game if game is not None else None

async def insert_game_data(game: GameDataBase = None, session: AsyncSession = None, **kwargs):
    db_game = GameData(**(game.model_dump() if game is not None else kwargs))

    try:
        session.add(db_game)
        await session.commit()

    except:
        return {"error": "Exists in database"}
    
    return game