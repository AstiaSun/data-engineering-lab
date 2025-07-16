from datetime import datetime

from pydantic import BaseModel, Field


class ReviewMessage(BaseModel):
    customer_id: int
    review_id: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
