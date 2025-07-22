from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

from ..constants import DEFAULT_BATCH_SIZE
from ..db import DBSession
from ..models import Base


class Uploader(ABC):
    _MODEL: ClassVar[type[Base]]

    def __init__(self, *, batch_size: int = DEFAULT_BATCH_SIZE):
        self._db = DBSession()
        self._batch_size = batch_size
        self._batch: list[Base] = []

    @abstractmethod
    def _upload(self, source_path): ...

    def _reset_batch(self):
        self._batch.clear()

    def upload(self, source_path: Path):
        self._reset_batch()
        with self._db:
            self._upload(source_path)
