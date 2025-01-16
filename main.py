from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from googleapiclient.discovery import build

from constants import GOOGLE_DK

from routes.game import game_router
from routes.account import account_router
from routes.multiplayer import multiplayer_router


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"]
)

handler = Mangum(app)

app.include_router(game_router)
app.include_router(account_router)
app.include_router(multiplayer_router)

# Custom Google Search Engine
app.search_service = build("customsearch", "v1", developerKey=GOOGLE_DK)


@app.get("/")
async def root():
    return {"message": "Check /docs for documentation"}