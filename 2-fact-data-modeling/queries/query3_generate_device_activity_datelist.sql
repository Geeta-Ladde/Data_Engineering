-- Query 3: Cumulative query to generate device_activity_datelist from events
-- This query builds up the device activity history for each user by browser_type

INSERT INTO user_devices_cumulated
WITH yesterday AS (
    SELECT 
        user_id,
        device_activity_datelist,
        date
    FROM user_devices_cumulated
    WHERE date = DATE('{{ ds }}') - INTERVAL '1' DAY
),
today AS (
    SELECT 
        e.user_id,
        d.browser_type,
        DATE(CAST(e.event_time AS TIMESTAMP)) AS event_date
    FROM events e
    JOIN devices d ON e.device_id = d.device_id
    WHERE DATE(CAST(e.event_time AS TIMESTAMP)) = DATE('{{ ds }}')
    GROUP BY e.user_id, d.browser_type, DATE(CAST(e.event_time AS TIMESTAMP))
)
SELECT 
    COALESCE(y.user_id, t.user_id) AS user_id,
    CASE 
        WHEN y.device_activity_datelist IS NULL THEN 
            MAP_FROM_ENTRIES(ARRAY[ROW(t.browser_type, ARRAY[t.event_date])])
        WHEN t.user_id IS NULL THEN 
            y.device_activity_datelist
        ELSE 
            MAP_CONCAT(
                y.device_activity_datelist,
                MAP_FROM_ENTRIES(
                    ARRAY[ROW(
                        t.browser_type,
                        ARRAY_UNION(
                            COALESCE(y.device_activity_datelist[t.browser_type], ARRAY[]),
                            ARRAY[t.event_date]
                        )
                    )]
                )
            )
    END AS device_activity_datelist,
    DATE('{{ ds }}') AS date
FROM yesterday y
FULL OUTER JOIN today t ON y.user_id = t.user_id;
