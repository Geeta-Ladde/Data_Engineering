-- Query 7: LeBron James longest streak of 10+ point games
WITH lebron_games AS (
    SELECT 
        player_name,
        game_id,
        pts,
        CASE WHEN pts >= 10 THEN 1 ELSE 0 END AS scored_10_plus,
        ROW_NUMBER() OVER (PARTITION BY player_name ORDER BY game_id) AS game_number
    FROM game_details
    WHERE player_name = 'LeBron James'
),
streak_groups AS (
    SELECT 
        player_name,
        game_id,
        pts,
        scored_10_plus,
        game_number,
        game_number - SUM(CASE WHEN scored_10_plus = 1 THEN 1 ELSE 0 END) OVER (
            PARTITION BY player_name 
            ORDER BY game_id 
            ROWS UNBOUNDED PRECEDING
        ) AS streak_group
    FROM lebron_games
),
streak_lengths AS (
    SELECT 
        player_name,
        streak_group,
        COUNT(*) AS streak_length,
        MIN(game_id) AS streak_start_game,
        MAX(game_id) AS streak_end_game,
        MIN(pts) AS min_points,
        MAX(pts) AS max_points,
        ROUND(AVG(pts), 2) AS avg_points
    FROM streak_groups
    WHERE scored_10_plus = 1
    GROUP BY player_name, streak_group
),
ranked_streaks AS (
    SELECT 
        player_name,
        streak_length,
        streak_start_game,
        streak_end_game,
        min_points,
        max_points,
        avg_points,
        RANK() OVER (ORDER BY streak_length DESC) AS streak_rank
    FROM streak_lengths
)
SELECT 
    player_name,
    streak_length AS longest_streak_10plus_points,
    streak_start_game,
    streak_end_game,
    min_points,
    max_points,
    avg_points
FROM ranked_streaks
WHERE streak_rank = 1;
