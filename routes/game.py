from fastapi import APIRouter, Depends, Request
import requests
from sqlalchemy.ext.asyncio import AsyncSession

from models.games import get_game_data, insert_game_data
from database import get_db_session
from constants import *

game_router = APIRouter(
    prefix="/game"
)

platformsDict = {
    "PC": 6,
    "Mac": 14,
    "PS4": 48,
    "Xbox One": 49,
    "Switch": 130,
    "PS3": 9,
    "PS5": 167,
    "Xbox X|S": 169
}

genresDict = {
    "Indie": 32,
    "Puzzle": 9,
    "Adventure": 31,
    "RPG": 12,
    "Shooter": 5,
    "Sports": 14,
    "Strategy": 15,
    "Fighting": 4,
    "MOBA": 36,
    "Platformer": 8,
    "Rhythm": 7,
    "Racing": 10
}

themesDict = {
    "Action": 1,
    "Fantasy": 17,
    "Sandbox": 33,
    "Horror": 19,
    "Thriller": 20,
    "Open world": 38,
    "Historical": 22,
    "Sci-Fi": 18,
    "Survival": 21,
    "Comedy": 27,
    "Drama": 31,
    "Business": 28,
    "Kids": 35,
    "Educational": 34,
    "Party": 40,
    "Mystery": 43,
    "Warfare": 39,
    "Non-fiction": 32
}

id_dicts = {
    "platforms": platformsDict,
    "genres": genresDict,
    "themes": themesDict
}

@game_router.get("/get-image")
async def _get_game_image(name: str, request: Request, session: AsyncSession = Depends(get_db_session)):
    return await locate_game_image(name=name, search_service=request.app.search_service, session=session)


@game_router.get("/query-games")
async def _query_games(platforms: str = None, genres: str = None, themes: str = None, rating: int = 0, session: AsyncSession = Depends(get_db_session)):
    igdbHeader = {"Client-ID": IGDB_CLIENT_ID,
          "Authorization": "Bearer " + IGDB_ACCESS_TOKEN}
    
    query = f"""fields name,genres.name,themes.name,platforms.name,rating,total_rating_count,summary;
                sort rating_count desc;
                where {cleanup_param('platforms', platforms)} 
                & {cleanup_param('genres', genres)} 
                & {cleanup_param('themes', themes)} 
                & rating > {rating}
                & rating != null
                & rating_count != null;
                limit 15;
    """
    response = requests.post(f'{IGDB_ENDPT}/games', **{"headers": igdbHeader, "data": query}).json()

    return response

def cleanup_param(param: str, value: str):
    if not value:
        return f"{param} != null"

    values = []

    for val in value.split(","):
        if val.lower().capitalize() in id_dicts[param].keys():
            values.append(str(id_dicts[param][val.lower().capitalize()]))

    return f"{param}=[{','.join(values)}]" if len(values) > 0 else f"{param} != null"

async def locate_game_image(name: str, search_service, session: AsyncSession):
    game = await get_game_data(name=name.lower(), session=session)
    if game is not None:
        return {"url": game.img,
                "info": "Found in database"}
    else:
        result = search_service.cse().list(
            q=name+" game wide image",
            cx=GOOGLE_CX,
            searchType='image',
            num=1,
            safe="off",
            rights="cc_publicdomain cc_attribute"
        ).execute()
        if not result:
            return {"url": "https://upload.wikimedia.org/wikipedia/commons/4/49/A_black_image.jpg",
                    "info": "exceeded search limit"}
        url = result["items"][0]["link"]
        
        await insert_game_data(name=name.lower(), img=url, session=session)
        
        return {"url": url,
                "info": "Added to database"}