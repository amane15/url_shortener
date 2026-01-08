from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.exception import AppException
from .routers import urls, users
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


@app.exception_handler(AppException)
def app_exception_handler(_, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


app.include_router(urls.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "running"}
