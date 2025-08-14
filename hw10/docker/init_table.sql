CREATE KEYSPACE IF NOT EXISTS wikimedia
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE IF NOT EXISTS wikimedia.page_create (
    user_id int,
    domain text,
    page_title text,
    created_at timestamp,
    PRIMARY KEY (user_id, created_at)
);
