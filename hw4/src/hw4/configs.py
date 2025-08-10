from pydantic import BaseModel, Field, ConfigDict


class LoaderConfig(BaseModel):
    max_in_flight: int = Field(default=500)
    retry_delay: float = Field(default=0.2)
    max_retries: int = Field(default=3)

    model_config = ConfigDict(extra="forbid", frozen=True)
