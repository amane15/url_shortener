from .base import Base
from .user import User
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column


class URL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    short_code: Mapped[str] = mapped_column(
        String(), unique=True, index=True, nullable=False
    )
    original_url: Mapped[str] = mapped_column(String(), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
