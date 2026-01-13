import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or ""
REDIS_URL = os.getenv("REDIS_URL") or ""
COUNTER_KEY = os.getenv("COUNTER_KEY") or ""
COUNTER_RANGE_SIZE = int(os.getenv("COUNTER_RANGE_SIZE"))
FEISTEL_SECRET = os.getenv("FEISTEL_SECRET").encode() or ""
HOST = os.getenv("HOST")
