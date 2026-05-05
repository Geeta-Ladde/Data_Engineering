-- Query 5: DDL for hosts_cumulated table
-- This table tracks which dates each host experiences activity

CREATE TABLE hosts_cumulated (
    host VARCHAR,
    host_activity_datelist ARRAY<DATE>,
    date DATE,
    PRIMARY KEY (host, date)
);
