-- Query 6: Incremental query to generate host_activity_datelist
-- This query builds up the activity history for each host day by day

INSERT INTO hosts_cumulated
WITH yesterday AS (
    SELECT 
        host,
        host_activity_datelist,
        date
    FROM hosts_cumulated
    WHERE date = DATE('{{ ds }}') - INTERVAL '1' DAY
),
today AS (
    SELECT 
        host,
        DATE(CAST(event_time AS TIMESTAMP)) AS event_date
    FROM events
    WHERE DATE(CAST(event_time AS TIMESTAMP)) = DATE('{{ ds }}')
    GROUP BY host, DATE(CAST(event_time AS TIMESTAMP))
)
SELECT 
    COALESCE(y.host, t.host) AS host,
    CASE 
        WHEN y.host_activity_datelist IS NULL THEN ARRAY[t.event_date]
        WHEN t.host IS NULL THEN y.host_activity_datelist
        ELSE ARRAY_UNION(y.host_activity_datelist, ARRAY[t.event_date])
    END AS host_activity_datelist,
    DATE('{{ ds }}') AS date
FROM yesterday y
FULL OUTER JOIN today t ON y.host = t.host;
