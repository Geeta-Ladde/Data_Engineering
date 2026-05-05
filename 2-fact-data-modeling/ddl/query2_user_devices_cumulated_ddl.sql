-- Query 2: DDL for user_devices_cumulated table
-- This table tracks a user's active days by browser_type using a MAP structure

CREATE TABLE user_devices_cumulated (
    user_id BIGINT,
    device_activity_datelist MAP<VARCHAR, ARRAY<DATE>>,
    date DATE,
    PRIMARY KEY (user_id, date)
);

-- Alternative approach with browser_type as a column (multiple rows per user):
-- CREATE TABLE user_devices_cumulated (
--     user_id BIGINT,
--     browser_type VARCHAR,
--     activity_dates ARRAY<DATE>,
--     date DATE,
--     PRIMARY KEY (user_id, browser_type, date)
-- );
