from fastapi import APIRouter

router = APIRouter(prefix="/urls")


@router.get("/{short_code}")
async def redirect_to_original_url():
    pass


@router.post("/")
async def generate_short_url():
    pass
