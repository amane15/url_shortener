from typing import Annotated
from fastapi import APIRouter, Path, status
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from app.exception import BadRequestException
from app.internal.base62 import base62_encode
from app.internal.feistel import feistel_encrypt
from app.internal.url import validate_and_cannonicalize_url
from app.models.url import URL
from app.dependencies import DBDep, CounterDep
from app.schemas.urls import CreateUrlBody
from app.config import FEISTEL_SECRET, HOST
from datetime import datetime, timezone
from app.internal.get_current_user import CurrentUserDep

router = APIRouter(prefix="/urls")


@router.get("/{short_code}")
async def redirect_to_original_url(
    short_code: Annotated[str, Path(title="The short code of the original url")],
    db: DBDep,
):
    result = await db.execute(select(URL).where(URL.short_code == short_code))
    url = result.scalar_one_or_none()

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The short url with code {short_code} does not exist",
        )

    if url.expires_at < datetime.now(timezone.utc):
        raise BadRequestException(detail="Link is expired")

    return RedirectResponse(url=url.original_url, status_code=status.HTTP_302_FOUND)


@router.post("/")
async def generate_short_url(
    body: CreateUrlBody, current_user: CurrentUserDep, db: DBDep, counter: CounterDep
):
    try:
        validated_url = validate_and_cannonicalize_url(body.url)

        url_id = await counter.next()

        short_code = base62_encode(feistel_encrypt(url_id, FEISTEL_SECRET))

        url = URL(
            short_code=short_code,
            original_url=validated_url,
            expires_at=body.expires_at,
            user_id=current_user.id,
        )
        db.add(url)
        await db.commit()
        await db.refresh(url)

        return {"short_code": f"{HOST}/urls/{url.short_code}"}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
