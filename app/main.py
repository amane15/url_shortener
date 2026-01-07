from fastapi import FastAPI
from .routers import urls
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.include_router(urls.router)


@app.get("/")
async def root():
    return {"message": "running"}
