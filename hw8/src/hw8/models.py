from datetime import datetime, UTC
from typing import Any

from pydantic import BaseModel, BeforeValidator, ConfigDict, field_validator
from typing_extensions import Annotated


def _override_value_to_current_time(_: Any) -> datetime:
    return datetime.now(UTC)

def _override_empty_str_with_null(value: Any) -> Any:
    if isinstance(value, str) and not value:
        return None
    return value


OptionalTweetID = Annotated[int | None, BeforeValidator(_override_empty_str_with_null)]
DatetimeNow = Annotated[datetime, BeforeValidator(_override_value_to_current_time)]

class Tweet(BaseModel):
    tweet_id: int
    author_id: str
    inbound: bool
    created_at: DatetimeNow
    text: str
    response_tweet_id: list[int]
    in_response_to_tweet_id: OptionalTweetID

    model_config = ConfigDict(frozen=True)

    @field_validator("response_tweet_id", mode="before")
    @classmethod
    def parse_string_to_list(cls, value: Any) -> Any:
        if isinstance(value, str):
            if not value:
                return []
            return list(map(int, value.split(',')))
        return value
