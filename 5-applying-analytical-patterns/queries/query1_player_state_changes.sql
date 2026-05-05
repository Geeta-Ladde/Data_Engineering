-- Query 1: State Change Tracking
WITH season_spine AS (
    SELECT GENERATE_SERIES(
        (SELECT MIN(season) FROM player_seasons),
        (SELECT MAX(season) FROM player_seasons)
    ) AS season
),
player_list AS (
    SELECT DISTINCT player_name FROM players
),
player_season_grid AS (
    SELECT p.player_name, s.season
    FROM player_list p
    CROSS JOIN season_spine s
),
player_activity AS (
    SELECT 
        psg.player_name,
        psg.season,
        EXISTS (
            SELECT 1
            FROM players_scd ps
            WHERE ps.player_name = psg.player_name
                AND ps.is_active = TRUE
                AND psg.season BETWEEN ps.start_season AND COALESCE(ps.end_season, 9999)
        ) AS is_active
    FROM player_season_grid psg
),
lagged_activity AS (
    SELECT 
        player_name,
        season,
        is_active,
        LAG(is_active) OVER (PARTITION BY player_name ORDER BY season) AS prev_is_active
    FROM player_activity
)
SELECT 
    player_name,
    season,
    CASE 
        WHEN prev_is_active IS NULL AND is_active = TRUE THEN 'New'
        WHEN prev_is_active = TRUE AND is_active = FALSE THEN 'Retired'
        WHEN prev_is_active = TRUE AND is_active = TRUE THEN 'Continued Playing'
        WHEN prev_is_active = FALSE AND is_active = TRUE THEN 'Returned from Retirement'
        WHEN prev_is_active = FALSE AND is_active = FALSE THEN 'Stayed Retired'
        ELSE 'Unknown'
    END AS player_state
FROM lagged_activity
WHERE prev_is_active IS NOT NULL OR is_active = TRUE
ORDER BY player_name, season;
