import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import pandas as pd


class Reporter(ABC):
    @abstractmethod
    def report(self, data: Any): ...


class CSVReporter(Reporter):
    def __init__(self):
        self._output_directory: Path = Path.cwd() / "reporter"
        self._output_directory.mkdir(exist_ok=True)

    def report(self, data: Any, *, file_name: str | None = None, **df_kwargs: Any):
        file_name = file_name or str(uuid.uuid4())
        file_path = self._output_directory / f"{file_name}.csv"
        pd.DataFrame(data, **df_kwargs).to_csv(file_path, index=False)
        print(f"Exported to {file_path.relative_to(Path.cwd())}")
