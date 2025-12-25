from datetime import datetime
from .base import Base
from sqlalchemy import Integer, String, LargeBinary, text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "app_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    version: Mapped[int] = mapped_column(Integer, default=1, server_default=text("1"))
