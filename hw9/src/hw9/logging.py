import logging
from datetime import datetime

from ..constants import OUTPUT_PATH


def setup_logging(level: int = logging.INFO):
    logs_base_path = OUTPUT_PATH / ".logs"
    logs_base_path.mkdir(exist_ok=True)
    logging.basicConfig(
        filename=logs_base_path / f"{datetime.now().isoformat()}.log",
        encoding="utf-8",
        level=level,
        format="%(asctime)s - %(levelname)s:%(name)s - %(message)s",
    )
    return logging.getLogger("main")
