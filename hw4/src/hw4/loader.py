import dataclasses
import logging
from typing import Any

from cassandra.concurrent import execute_concurrent_with_args

from .constants import CASSANDRA_CONCURRENT_REQUESTS
from .db.db import session
from .db.queries import QueryHandler
from .models import AdEventRecord

logger = logging.getLogger("pipeline")


@dataclasses.dataclass
class LoaderStats:
    success_count: int = 0
    fail_count: int = 0


class AdEventsLoader:
    """AdEventsLoader is responsible ingesting records to Cassandra DB"""

    def __init__(self, statements: list[QueryHandler]):
        """
        :param statements: list of handlers, which extracts and transforms needed data
            from a single row for a specific table in DB
        """
        self._statements = statements
        self._statement_params: list[list[Any]] = [
            [] for _ in range(len(self._statements))
        ]
        self._stats = LoaderStats()

    @property
    def success_count(self) -> int:
        return self._stats.success_count

    @property
    def fail_count(self) -> int:
        return self._stats.fail_count

    @property
    def batch_sizes(self) -> list[int]:
        """
        return number of collected parameters for each statement
        """
        return [len(params) for params in self._statement_params]

    def add_statement_params(self, ad_event: AdEventRecord):
        """extracts needed data for each table (parameters) from a record and add them to batches"""
        for stmt_position, stmt_obj in enumerate(self._statements):
            bound_params = stmt_obj.bind_from_event(ad_event)
            if bound_params is None:
                continue
            self._statement_params[stmt_position].append(bound_params)

    def execute_statements(self):
        """stores collected data in the database and clears batches"""
        for statement_id in range(len(self._statements)):
            self.execute_statement(statement_id)

    def execute_statement(self, statement_id: int):
        results = execute_concurrent_with_args(
            session,
            self._statements[statement_id].statement,
            self._statement_params[statement_id],
            concurrency=CASSANDRA_CONCURRENT_REQUESTS,
        )

        for success, result in results:
            if not success:
                self._stats.fail_count += 1
                logger.exception(result)
            else:
                self._stats.success_count += 1
        self._statement_params[statement_id] = []
