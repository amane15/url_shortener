from fastapi import FastAPI
from .routers import urls

app = FastAPI()

app.include_router(urls.router)


@app.get("/")
async def root():
    return {"message": "running"}
