-- Query 7: DDL for host_activity_reduced monthly fact table
-- This is a reduced/aggregated fact table at the monthly grain

CREATE TABLE host_activity_reduced (
    host VARCHAR,
    month DATE,
    hit_array ARRAY<BIGINT>,
    unique_visitors_array ARRAY<BIGINT>,
    PRIMARY KEY (host, month)
);

-- Explanation:
-- month: The month being aggregated (e.g., '2023-01-01' for January 2023)
-- hit_array: Array of daily hit counts (COUNT(1)) for each day of the month
-- unique_visitors_array: Array of daily unique visitor counts (COUNT(DISTINCT user_id)) for each day
