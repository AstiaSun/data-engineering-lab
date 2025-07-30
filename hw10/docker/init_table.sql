CREATE KEYSPACE IF NOT EXISTS wikimedia
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE IF NOT EXISTS wikimedia.page_create (
    id UUID PRIMARY KEY,
    domain TEXT,
    title TEXT,
    user TEXT,
    timestamp TIMESTAMP
);
