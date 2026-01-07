from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.session import get_db

DBDep = Annotated[AsyncSession, Depends(get_db)]
