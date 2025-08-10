import dataclasses
import logging
from collections import deque

from cassandra.cluster import Session

from .configs import LoaderConfig
from .db.queries import QueryHandler
from .models import AdEventRecord

logger = logging.getLogger(__file__)


@dataclasses.dataclass
class LoaderStats:
    success_count: int = 0
    fail_count: int = 0


class AdEventsLoader:
    def __init__(
        self,
        session: Session,
        statements: list[QueryHandler],
        *,
        config: LoaderConfig | None = None,
    ):
        self._session = session
        self._config = config or LoaderConfig()
        self._statements = statements
        self._in_flight = deque()
        self._stats = LoaderStats()

    @property
    def success_count(self) -> int:
        return self._stats.success_count

    @property
    def fail_count(self) -> int:
        return self._stats.fail_count

    def _wait_for_slot(self):
        while len(self._in_flight) >= self._config.max_in_flight:
            self._complete_one()

    def _complete_one(self):
        future = self._in_flight.popleft()
        try:
            future.result()
            self._stats.success_count += 1
        except Exception:
            self._stats.fail_count += 1
            logger.exception("Insert failed:")

    def insert_async(self, ad_event: AdEventRecord):
        for stmt_obj in self._statements:
            self._wait_for_slot()
            bound_params = stmt_obj.bind_from_event(ad_event)
            if bound_params is None:
                continue
            future = self._session.execute_async(stmt_obj.statement, bound_params)
            self._in_flight.append(future)

    def flush(self):
        while self._in_flight:
            self._complete_one()
