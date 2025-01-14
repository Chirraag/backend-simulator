import os

from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("mongo-url")
DB_NAME = os.getenv("db-name")
