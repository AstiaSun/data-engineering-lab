import csv
import uuid
from datetime import datetime
from pathlib import Path
from typing import ClassVar

from tqdm import tqdm

from .abstract import Uploader
from .utils import to_bool, to_timestamp
from ..models import AdEvent


class AdEventUploader(Uploader):
    _MODEL: ClassVar[type[AdEvent]] = AdEvent

    def _upload(self, source_path: Path):
        line_count = sum(1 for _ in source_path.open()) - 1

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
        with (
            source_path.open() as csv_file,
            tqdm(mininterval=1, desc=f"Loading {self._MODEL.__table__}", total=line_count) as progress_bar
        ):
            stream_reader = csv.reader(csv_file)
            header = next(stream_reader)
            filtered_columns_idx = [header.index(column) for column in ad_event_header]
            ad_event_header[-1] = "CampaignID"
            for record in stream_reader:
                if len(self._batch) >= self._batch_size:
                    self._db.insert_batch(self._batch)
                    progress_bar.update(len(self._batch))
                    self._reset_batch()
                ad_event_values = [record[idx] for idx in filtered_columns_idx]
                ad_event_values[-1] = ad_event_values[-1].removeprefix("Campaign_")
                params = dict(zip(ad_event_header, ad_event_values))
                for column, transform in filtered_columns_transformers.items():
                    params[column] = transform(params[column])
                self._batch.append(AdEvent(**params))
            self._db.insert_batch(self._batch)
            progress_bar.update(len(self._batch))