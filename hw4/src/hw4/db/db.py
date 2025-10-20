import atexit

from cassandra import ConsistencyLevel
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import EXEC_PROFILE_DEFAULT, Cluster, ExecutionProfile, Session
from cassandra.cqlengine import connection
from cassandra.policies import (
    DCAwareRoundRobinPolicy,
    DowngradingConsistencyRetryPolicy,
)

from ..constants import CASSANDRA_HOST, CASSANDRA_PASSWORD, CASSANDRA_USER

cluster = Cluster(
    [CASSANDRA_HOST],
    auth_provider=PlainTextAuthProvider(
        username=CASSANDRA_USER, password=CASSANDRA_PASSWORD
    ),
    execution_profiles={
        EXEC_PROFILE_DEFAULT: ExecutionProfile(
            load_balancing_policy=DCAwareRoundRobinPolicy(),
            retry_policy=DowngradingConsistencyRetryPolicy(),
            consistency_level=ConsistencyLevel.LOCAL_ONE,
        ),
    },
    idle_heartbeat_interval=30,
    protocol_version=5,
)
session: Session = cluster.connect()
connection.set_session(session)


@atexit.register
def shutdown_cassandra():
    session.shutdown()
    cluster.shutdown()
