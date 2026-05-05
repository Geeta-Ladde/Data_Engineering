-- ============================================================================
-- HOMEWORK ANALYSIS QUERIES
-- ============================================================================

-- Question 1: What is the average number of web events of a session 
--             from a user on Tech Creator?
-- ============================================================================

-- Average events per session for ALL Tech Creator hosts
SELECT 
    'All Tech Creator Hosts' as category,
    COUNT(*) as total_sessions,
    AVG(num_events) as avg_events_per_session,
    MIN(num_events) as min_events_per_session,
    MAX(num_events) as max_events_per_session,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY num_events) as median_events_per_session
FROM sessionized_events
WHERE host LIKE '%.techcreator.io';


-- Question 2: Compare results between different hosts
-- ============================================================================

-- Detailed comparison by specific host
SELECT 
    host,
    COUNT(*) as total_sessions,
    COUNT(DISTINCT ip) as unique_users,
    AVG(num_events) as avg_events_per_session,
    MIN(num_events) as min_events_per_session,
    MAX(num_events) as max_events_per_session,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY num_events) as median_events_per_session,
    SUM(num_events) as total_events
FROM sessionized_events
WHERE host IN (
    'zachwilson.techcreator.io',
    'zachwilson.tech',
    'lulu.techcreator.io'
)
GROUP BY host
ORDER BY avg_events_per_session DESC;


-- ============================================================================
-- ADDITIONAL INSIGHTS
-- ============================================================================

-- Session duration analysis (in minutes)
SELECT 
    host,
    COUNT(*) as total_sessions,
    AVG(EXTRACT(EPOCH FROM (session_end - session_start))/60) as avg_session_duration_minutes,
    MIN(EXTRACT(EPOCH FROM (session_end - session_start))/60) as min_session_duration_minutes,
    MAX(EXTRACT(EPOCH FROM (session_end - session_start))/60) as max_session_duration_minutes
FROM sessionized_events
WHERE host IN (
    'zachwilson.techcreator.io',
    'zachwilson.tech',
    'lulu.techcreator.io'
)
GROUP BY host
ORDER BY avg_session_duration_minutes DESC;


-- Top 10 most active users (by session count)
SELECT 
    ip,
    host,
    COUNT(*) as session_count,
    AVG(num_events) as avg_events_per_session,
    SUM(num_events) as total_events
FROM sessionized_events
WHERE host IN (
    'zachwilson.techcreator.io',
    'zachwilson.tech',
    'lulu.techcreator.io'
)
GROUP BY ip, host
ORDER BY session_count DESC
LIMIT 10;


-- Distribution of session sizes
SELECT 
    host,
    CASE 
        WHEN num_events = 1 THEN '1 event'
        WHEN num_events BETWEEN 2 AND 5 THEN '2-5 events'
        WHEN num_events BETWEEN 6 AND 10 THEN '6-10 events'
        WHEN num_events BETWEEN 11 AND 20 THEN '11-20 events'
        WHEN num_events > 20 THEN '20+ events'
    END as session_size_bucket,
    COUNT(*) as session_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY host), 2) as percentage
FROM sessionized_events
WHERE host IN (
    'zachwilson.techcreator.io',
    'zachwilson.tech',
    'lulu.techcreator.io'
)
GROUP BY host, session_size_bucket
ORDER BY host, session_size_bucket;


-- Time-based analysis: Sessions by hour of day
SELECT 
    host,
    EXTRACT(HOUR FROM session_start) as hour_of_day,
    COUNT(*) as session_count,
    AVG(num_events) as avg_events_per_session
FROM sessionized_events
WHERE host IN (
    'zachwilson.techcreator.io',
    'zachwilson.tech',
    'lulu.techcreator.io'
)
GROUP BY host, EXTRACT(HOUR FROM session_start)
ORDER BY host, hour_of_day;


-- Overall summary statistics
SELECT 
    COUNT(*) as total_sessions,
    COUNT(DISTINCT ip) as unique_ips,
    COUNT(DISTINCT host) as unique_hosts,
    AVG(num_events) as overall_avg_events_per_session,
    SUM(num_events) as total_events_processed
FROM sessionized_events;
