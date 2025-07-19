from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel, field_validator, ConfigDict

PARTITION_KEY_FORMAT = "%d_%m_%Y_%H_%M"


class Tweet(BaseModel):
    tweet_id: int
    author_id: str
    inbound: bool
    created_at: datetime
    text: str
    response_tweet_id: list[int]
    in_response_to_tweet_id: int | None

    model_config = ConfigDict(frozen=True, extra="forbid")

    def get_partition_key(self) -> str:
        return self.created_at.strftime(PARTITION_KEY_FORMAT)


class PartitionKey(BaseModel):
    created_at: str

    model_config = ConfigDict(frozen=True, extra="forbid")

    @field_validator("created_at", mode="after")
    @classmethod
    def verify_partition_key(cls, created_at: str):
        datetime.strptime(created_at, PARTITION_KEY_FORMAT)
        return created_at


@dataclass(frozen=True)
class TweetByKey:
    key: str
    tweet: Tweet
