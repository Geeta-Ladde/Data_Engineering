-- Query 4: Convert device_activity_datelist to datelist_int
-- This converts the date arrays into integer representations for efficient storage
-- Each bit represents whether the user was active on that day

WITH date_array_expanded AS (
    SELECT 
        user_id,
        browser_type,
        activity_date,
        date
    FROM user_devices_cumulated
    CROSS JOIN UNNEST(
        TRANSFORM_KEYS(device_activity_datelist, (k, v) -> k)
    ) AS browser_type
    CROSS JOIN UNNEST(
        device_activity_datelist[browser_type]
    ) AS activity_date
    WHERE date = DATE('{{ ds }}')
)
SELECT 
    user_id,
    browser_type,
    -- Convert dates to integers where each bit represents a day
    -- Day 0 is the earliest date in the dataset
    MAP_FROM_ENTRIES(
        ARRAY_AGG(
            ROW(
                browser_type,
                CAST(SUM(
                    POW(2, DATE_DIFF('day', DATE('2023-01-01'), activity_date))
                ) AS BIGINT)
            )
        )
    ) AS device_activity_datelist_int,
    date
FROM date_array_expanded
GROUP BY user_id, browser_type, date;
