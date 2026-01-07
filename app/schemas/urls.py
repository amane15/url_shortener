from pydantic import (
    BaseModel,
    model_validator,
)
from datetime import datetime, timedelta


def parse_expires_in(value: str) -> datetime:
    parts = value.strip().split(" ")
    if len(parts) != 2:
        raise ValueError("expires_in must be '<number> <unit>'")

    number, unit = parts
    if not number.isdigit():
        raise ValueError("Duration must be positive integer")

    amount = int(number)
    if amount <= 0:
        raise ValueError("Duration must be greater than 0")

    unit = unit.lower()
    now = datetime.now()

    if unit == "d":
        return now + timedelta(days=amount)
    if unit == "m":
        return now + timedelta(days=30 * amount)
    if unit == "y":
        return now + timedelta(days=365 * amount)

    raise ValueError("Unit must be one of: d, m, y")


class CreateUrlBody(BaseModel):
    url: str
    seq: int
    expires_at: datetime

    @model_validator(mode="before")
    @classmethod
    def compute_expires_at(cls, data: dict):
        expires_in = data.pop("expires_in", None)
        if not expires_in:
            raise ValueError("expires_in is required")

        data["expires_at"] = parse_expires_in(expires_in)
        return data
