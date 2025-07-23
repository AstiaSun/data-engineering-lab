import csv
import re
import sys
from pathlib import Path

from tqdm import tqdm

from .abstract import Uploader
from ..models import Campaign


class CampaignsUploader(Uploader):
    def _upload(self, source_path: Path):
        """
        Uploads data from CSV file into 3 databases: Campaigns, Locations and Interests.
        The data is inserted by chunks following the next algorithm:

        1. Read the line from the file and parse it
        2. Get target location ID from DB
        3. If not exist, insert value into Locations table
        4. Get target interest ID from DB
        5. If not exist, insert value into Interests table
        6. Add campaign record to the batch
        7. If the batch is full, insert it the DB

        :param source_path: path to the CSV file with campaigns data
        """
        age_regex = re.compile(r"Age (\d+)-(\d+)")
        line_count = sum(1 for _ in source_path.open()) - 1
        with (
            source_path.open() as csv_file,
            tqdm(mininterval=1, desc=f"Loading {source_path.name}", total=line_count, file=sys.stdout) as progress_bar
        ):
            stream_reader = csv.reader(csv_file)
            header = next(stream_reader)
            targeting_criteria_idx = header.index("TargetingCriteria")
            header.pop(targeting_criteria_idx)
            for record in stream_reader:
                if len(self._batch) >= self._batch_size:
                    self._db.insert_batch(self._batch)
                    progress_bar.update(len(self._batch))
                    progress_bar.refresh()
                    self._reset_batch()
                targeting_criteria_raw = record.pop(targeting_criteria_idx)
                target_age_gap, target_interest_field, target_country = (
                    targeting_criteria_raw.split(",")
                )
                target_interest = self._db.get_interest(target_interest_field.strip())
                target_location = self._db.get_location(target_country.strip())

                age_parser = age_regex.match(target_age_gap)
                campaign = Campaign(
                    TargetAgeMin=int(age_parser.group(1)),
                    TargetAgeMax=int(age_parser.group(2)),
                    TargetInterestID=target_interest.InterestID,
                    TargetLocationID=target_location.LocationID,
                    **dict(zip(header, record)),
                )
                self._batch.append(campaign)
            self._db.insert_batch(self._batch)
            progress_bar.update(len(self._batch))
            progress_bar.close()
