from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME

if not MONGO_URI:
    raise ValueError("MONGO_URI not set")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]