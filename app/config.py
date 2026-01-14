import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or ""
REDIS_COUNTER_URL = os.getenv("REDIS_COUNTER_URL") or ""
REDIS_CACHE_URL = os.getenv("REDIS_CACHE_URL") or ""
COUNTER_KEY = os.getenv("COUNTER_KEY") or ""
COUNTER_RANGE_SIZE = int(os.getenv("COUNTER_RANGE_SIZE"))
FEISTEL_SECRET = os.getenv("FEISTEL_SECRET").encode() or ""
HOST = os.getenv("HOST")
JWT_ACCESS_SECRET = os.getenv("JWT_ACCESS_SECRET")
JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET")
