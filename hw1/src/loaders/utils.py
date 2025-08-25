from datetime import datetime


def to_bool(s: str) -> bool:
    return s == "True"


def to_timestamp(s: str) -> datetime | None:
    return datetime.fromisoformat(s) if s else None
