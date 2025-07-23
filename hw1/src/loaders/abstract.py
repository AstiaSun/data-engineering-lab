from abc import ABC, abstractmethod
from pathlib import Path

from ..constants import DEFAULT_BATCH_SIZE
from ..db import DBSession
from ..models import Base


class Uploader(ABC):
    """base class for data loaders from file to SQL database"""

    def __init__(self, *, batch_size: int = DEFAULT_BATCH_SIZE):
        self._db = DBSession()
        self._batch_size = batch_size
        self._batch: list[Base] = []

    @abstractmethod
    def _upload(self, source_path): ...

    def _reset_batch(self):
        self._batch.clear()

    def upload(self, source_path: Path):
        """extracts data from the file and loads it to database
        :param source_path: path to the file
        """
        self._reset_batch()
        with self._db:
            self._upload(source_path)
