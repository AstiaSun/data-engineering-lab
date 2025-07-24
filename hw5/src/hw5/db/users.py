from typing import Any

from .client import db


async def get(user_id: int) -> dict[str, Any]:
    return await db.users.find_one({"UserID": user_id})
