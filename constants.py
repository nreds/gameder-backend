import dotenv
import os

dotenv.load_dotenv()

GOOGLE_DK = os.getenv("GOOGLE_DK")
GOOGLE_CX = os.getenv("GOOGLE_CX")
IGDB_CLIENT_ID = os.getenv("IGDB_CLIENT_ID")
IGDB_CLIENT_SECRET = os.getenv("IGDB_CLIENT_SECRET")
IGDB_ACCESS_TOKEN = os.getenv("IGDB_ACCESS_TOKEN")
IGDB_ENDPT = "https://api.igdb.com/v4"
IMG_DB_STRING = os.getenv("IMG_DB_STRING")
DBURL = os.getenv("DB_URL")