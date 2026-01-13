from typing import Annotated
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.session import get_db
from app.internal.range_counter import RangeCounter
from app.internal.redis import get_counter

DBDep = Annotated[AsyncSession, Depends(get_db)]
CounterDep = Annotated[RangeCounter, Depends(get_counter)]
