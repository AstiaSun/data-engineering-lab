import csv
from pathlib import Path
from typing import ClassVar

from tqdm import tqdm

from .abstract import Uploader
from ..constants import DEFAULT_BATCH_SIZE
from ..models import User, UserInterests


class UserUploader(Uploader):
    _MODEL: ClassVar[type[User]] = User

    def __init__(self, *, batch_size: int = DEFAULT_BATCH_SIZE):
        super().__init__(batch_size=batch_size)
        self._user_interests_batch: list[UserInterests] = []

    def _reset_batch(self):
        super()._reset_batch()
        self._user_interests_batch.clear()

    def _is_batch_full(self):
        return len(self._user_interests_batch) >= self._batch_size or len(self._batch) >= self._batch_size

    def _upload(self, source_path: Path):
        line_count = sum(1 for _ in source_path.open()) - 1
        with (
            source_path.open() as csv_file,
            tqdm(mininterval=1, desc=f"Loading {self._MODEL.__table__}", total=line_count) as progress_bar
        ):
            stream_reader = csv.reader(csv_file)
            header = next(stream_reader)
            interests_idx = header.index("Interests")
            location_idx = header.index("Location")
            header.pop(interests_idx)
            header.pop(location_idx)
            for line in stream_reader:
                if self._is_batch_full():
                    self._db.insert_batch(self._batch)
                    self._db.insert_batch(self._user_interests_batch)
                    progress_bar.update(len(self._batch))
                    self._reset_batch()
                interests = line.pop(interests_idx)
                for interest_name in interests.split(","):
                    interest = self._db.get_interest(interest_name.strip())
                    user_interest = UserInterests(UserID=int(line[0]), InterestID=interest.InterestID)
                    self._user_interests_batch.append(user_interest)
                location = self._db.get_location(line.pop(location_idx))
                user = User(LocationID=location.LocationID, **dict(zip(header, line)))
                self._batch.append(user)
            self._db.insert_batch(self._batch)
            self._db.insert_batch(self._user_interests_batch)
            progress_bar.update(len(self._batch))
