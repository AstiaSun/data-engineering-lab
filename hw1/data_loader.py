import csv
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, Engine, select
from sqlalchemy.orm import Session

from constants import SQLALCHEMY_DB_URL, DATASET_PATH
from hw1.models import Base, Campaign, AdEvent, UserInterests, User


def stream_campaigns(source_path: Path) -> Generator[Campaign, None, None]:
    age_regex = re.compile(r"Age (\d+)-(\d+)")

    with open(source_path) as csv_file:
        stream_reader = csv.reader(csv_file)
        header = next(stream_reader)
        targeting_criteria_idx = header.index("TargetingCriteria")
        header.pop(targeting_criteria_idx)
        for line in stream_reader:
            targeting_criteria_raw = line.pop(targeting_criteria_idx)
            target_age_gap, target_interest, target_country = (
                targeting_criteria_raw.split(",")
            )
            age_parser = age_regex.match(target_age_gap)
            yield Campaign(
                TargetAgeMin=int(age_parser.group(1)),
                TargetAgeMax=int(age_parser.group(2)),
                TargetInterest=target_interest,
                TargetLocation=target_country,
                **dict(zip(header, line)),
            )


def to_bool(s: str) -> bool:
    return s == "True"


def to_timestamp(s: str) -> datetime | None:
    return datetime.fromisoformat(s) if s else None


def stream_ad_events(
    engine: Engine, source_path: Path
) -> Generator[AdEvent, None, None]:
    with open(source_path) as csv_file:
        stream_reader = csv.reader(csv_file)
        header = next(stream_reader)
        filtered_columns_transformers = {
            "EventID": uuid.UUID,
            "UserID": None,
            "Device": None,
            "Timestamp": datetime.fromisoformat,
            "BidAmount": float,
            "AdCost": float,
            "WasClicked": to_bool,
            "ClickTimestamp": to_timestamp,
            "AdRevenue": float,
        }
        filtered_columns = list(filtered_columns_transformers.keys())
        ad_event_headers = [*filtered_columns, "CampaignID"]
        filtered_columns_idx = [header.index(column) for column in filtered_columns]
        campaign_columns = [
            "AdvertiserName",
            "CampaignName",
            "CampaignStartDate",
            "CampaignEndDate",
        ]
        campaign_headers_idx = [header.index(column) for column in campaign_columns]
        for line in stream_reader:
            campaign_id_query = (
                select(Campaign.CampaignID)
                .where(Campaign.CampaignName == line[campaign_headers_idx[1]])
                .where(Campaign.AdvertiserName == line[campaign_headers_idx[0]])
            )
            with engine.connect() as connection:
                (campaign_id,) = connection.execute(campaign_id_query).first()
            ad_event_values = [line[idx] for idx in filtered_columns_idx]
            ad_event_values.append(campaign_id)
            params = dict(zip(ad_event_headers, ad_event_values))
            for column, transformer in filtered_columns_transformers.items():
                if transformer:
                    params[column] = transformer(params[column])
            yield AdEvent(**params)


def stream_users(source_path: Path) -> Generator[User | UserInterests, None, None]:
    with open(source_path) as csv_file:
        stream_reader = csv.reader(csv_file)
        header = next(stream_reader)
        interests_idx = header.index("Interests")
        header.pop(interests_idx)
        dropped_field_idx = header.index("SignupDate")
        header.pop(dropped_field_idx)
        for line in stream_reader:
            interests = line.pop(interests_idx)
            line.pop(dropped_field_idx)
            yield User(**dict(zip(header, line)))
            for interest in interests.split(","):
                yield UserInterests(UserID=line[0], Interest=interest)


def db_insert_from_stream(
    engine: Engine, data_stream: Generator[Base, None, None], batch_size: int = 1000
):
    with Session(engine) as session:
        current_size = 0
        batch: list[Base | None] = [None] * batch_size
        for model in data_stream:
            batch[current_size] = model
            current_size += 1

            if current_size >= batch_size:
                session.add_all(batch)
                session.commit()
                current_size = 0

        if current_size > 0:
            session.add_all(batch[:current_size])
            session.commit()


def upload_dataset(engine: Engine):
    db_insert_from_stream(engine, stream_campaigns(DATASET_PATH / "campaigns.csv"))
    db_insert_from_stream(engine, stream_users(DATASET_PATH / "users.csv"))
    db_insert_from_stream(
        engine, stream_ad_events(engine, DATASET_PATH / "ad_events.csv")
    )


def main():
    engine = create_engine(SQLALCHEMY_DB_URL, echo=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    upload_dataset(engine)


if __name__ == "__main__":
    main()
