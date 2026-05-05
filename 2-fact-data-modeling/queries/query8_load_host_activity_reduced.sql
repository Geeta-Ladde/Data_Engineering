-- Query 8: Incremental query to load host_activity_reduced day-by-day
-- This builds the monthly aggregates incrementally as each day's data arrives

INSERT INTO host_activity_reduced
WITH daily_aggregate AS (
    SELECT 
        host,
        DATE(CAST(event_time AS TIMESTAMP)) AS event_date,
        COUNT(1) AS hit_count,
        COUNT(DISTINCT user_id) AS unique_visitors
    FROM events
    WHERE DATE(CAST(event_time AS TIMESTAMP)) = DATE('{{ ds }}')
    GROUP BY host, DATE(CAST(event_time AS TIMESTAMP))
),
yesterday AS (
    SELECT 
        host,
        month,
        hit_array,
        unique_visitors_array
    FROM host_activity_reduced
    WHERE month = DATE_TRUNC('month', DATE('{{ ds }}'))
)
SELECT 
    COALESCE(d.host, y.host) AS host,
    DATE_TRUNC('month', DATE('{{ ds }}')) AS month,
    CASE 
        WHEN y.hit_array IS NULL THEN 
            ARRAY_FILL(0, ARRAY[DAY(LAST_DAY(DATE('{{ ds }}')))]) || ARRAY[COALESCE(d.hit_count, 0)]
        WHEN d.host IS NULL THEN 
            y.hit_array
        ELSE 
            y.hit_array || ARRAY[d.hit_count]
    END AS hit_array,
    CASE 
        WHEN y.unique_visitors_array IS NULL THEN 
            ARRAY_FILL(0, ARRAY[DAY(LAST_DAY(DATE('{{ ds }}')))]) || ARRAY[COALESCE(d.unique_visitors, 0)]
        WHEN d.host IS NULL THEN 
            y.unique_visitors_array
        ELSE 
            y.unique_visitors_array || ARRAY[d.unique_visitors]
    END AS unique_visitors_array
FROM daily_aggregate d
FULL OUTER JOIN yesterday y ON d.host = y.host;

-- Alternative approach using MERGE or UPDATE logic:
-- MERGE INTO host_activity_reduced t
-- USING (
--     SELECT 
--         host,
--         DATE_TRUNC('month', DATE('{{ ds }}')) AS month,
--         COUNT(1) AS hit_count,
--         COUNT(DISTINCT user_id) AS unique_visitors,
--         DAY(DATE('{{ ds }}')) AS day_of_month
--     FROM events
--     WHERE DATE(CAST(event_time AS TIMESTAMP)) = DATE('{{ ds }}')
--     GROUP BY host
-- ) s
-- ON t.host = s.host AND t.month = s.month
-- WHEN MATCHED THEN 
--     UPDATE SET 
--         hit_array = ARRAY_CONCAT(t.hit_array, ARRAY[s.hit_count]),
--         unique_visitors_array = ARRAY_CONCAT(t.unique_visitors_array, ARRAY[s.unique_visitors])
-- WHEN NOT MATCHED THEN
--     INSERT (host, month, hit_array, unique_visitors_array)
--     VALUES (s.host, s.month, ARRAY[s.hit_count], ARRAY[s.unique_visitors]);
