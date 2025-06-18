import csv
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Generator, Type


from constants import DATASET_PATH
from hw1.db import DBSession
from hw1.models import Base, Campaign, AdEvent, UserInterests, User

CSV_NESTED_SEPARATOR = ";"
CSV_SEPARATOR = ","


def report_done(model: Type[Base]):
    print(f"{model.__tablename__}: done")


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
    report_done(Campaign)


def to_bool(s: str) -> bool:
    return s == "True"


def to_timestamp(s: str) -> datetime | None:
    return datetime.fromisoformat(s) if s else None


def stream_ad_events(source_path: Path):
    with open(source_path) as csv_file:
        header = csv_file.readline().strip().split(CSV_SEPARATOR)
        filtered_columns_transformers = {
            "EventID": uuid.UUID,
            "Timestamp": datetime.fromisoformat,
            "BidAmount": float,
            "AdCost": float,
            "WasClicked": to_bool,
            "ClickTimestamp": to_timestamp,
            "AdRevenue": float,
        }
        ad_event_header = [
            "EventID",
            "UserID",
            "Device",
            "Timestamp",
            "BidAmount",
            "AdCost",
            "WasClicked",
            "ClickTimestamp",
            "AdRevenue",
            "CampaignName",
        ]
        filtered_columns_idx = [header.index(column) for column in ad_event_header]
        ad_event_header[-1] = "CampaignID"
        while raw_line := csv_file.readline():
            line = (
                raw_line.replace("|", CSV_NESTED_SEPARATOR).strip().split(CSV_SEPARATOR)
            )
            ad_event_values = [line[idx] for idx in filtered_columns_idx]
            ad_event_values[-1] = ad_event_values[-1].removeprefix("Campaign_")
            params = dict(zip(ad_event_header, ad_event_values))
            for column, transformer in filtered_columns_transformers.items():
                params[column] = transformer(params[column])
            yield AdEvent(**params)
    report_done(AdEvent)


def stream_users(source_path: Path) -> Generator[User | UserInterests, None, None]:
    user_interests = []
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
                user_interests.append(UserInterests(UserID=line[0], Interest=interest))

    for user_interest in user_interests:
        yield user_interest
    report_done(User)


def db_insert_from_stream(
    db: DBSession, data_stream: Generator[Base, None, None], batch_size: int = 1000
):
    total_records_number = 0
    current_size = 0
    batch: list[Base | None] = [None] * batch_size

    for model in data_stream:
        batch[current_size] = model
        current_size += 1
        total_records_number += 1

        if current_size >= batch_size:
            db.insert_batch(batch=batch)
            current_size = 0
            if total_records_number % 100000 == 0:
                print(f"{model.__tablename__}: uploaded {total_records_number} records")

    if current_size > 0:
        db.insert_batch(batch[:current_size])


def upload_dataset(db_session: DBSession):
    db_insert_from_stream(db_session, stream_campaigns(DATASET_PATH / "campaigns.csv"))
    db_insert_from_stream(db_session, stream_users(DATASET_PATH / "users.csv"))
    db_insert_from_stream(db_session, stream_ad_events(DATASET_PATH / "ad_events.csv"))


def main():
    with DBSession() as db_session:
        upload_dataset(db_session)


if __name__ == "__main__":
    main()
