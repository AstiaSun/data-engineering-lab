import dataclasses
import logging
from typing import Any

from cassandra.cluster import Session
from cassandra.concurrent import execute_concurrent_with_args

from .constants import CASSANDRA_CONCURRENT_REQUESTS
from .db.queries import QueryHandler
from .models import AdEventRecord

logger = logging.getLogger("pipeline")


@dataclasses.dataclass
class LoaderStats:
    success_count: int = 0
    fail_count: int = 0


class AdEventsLoader:
    """AdEventsLoader is responsible ingesting records to Cassandra DB"""
    def __init__(self, session: Session, statements: list[QueryHandler]):
        """
        :param session: Cassandra DB session
        :param statements: list of handlers, which extracts and transforms needed data
            from a single row for a specific table in DB
        """
        self._session = session
        self._statements = statements
        self._statement_params: list[list[Any]] = [[]] * len(self._statements)
        self._stats = LoaderStats()

    @property
    def success_count(self) -> int:
        return self._stats.success_count

    @property
    def fail_count(self) -> int:
        return self._stats.fail_count

    @property
    def batch_size(self) -> int:
        """
        return the length of the biggest array of collected parameters.
        Each statement is considered to be executed separately, so we count each
        corresponding array of parameters as a separate batch.
        """
        return max(len(params) for params in self._statement_params)

    def save_statement_params(self, ad_event: AdEventRecord):
        """extracts needed data for each table (parameters) from a record and add them to batches"""
        for stmt_position, stmt_obj in enumerate(self._statements):
            bound_params = stmt_obj.bind_from_event(ad_event)
            if bound_params is None:
                continue
            self._statement_params[stmt_position].append(bound_params)

    def execute_statements(self):
        """stores collected data in the database and clears batches"""
        for statement, stmt_params in zip(self._statements, self._statement_params):
            results = execute_concurrent_with_args(
                self._session,
                statement.statement,
                stmt_params,
                concurrency=CASSANDRA_CONCURRENT_REQUESTS,
            )

            for success, result in results:
                if not success:
                    self._stats.fail_count += 1
                    logger.exception(result)
                else:
                    self._stats.success_count += 1
        self._statement_params = [[]] * len(self._statements)
