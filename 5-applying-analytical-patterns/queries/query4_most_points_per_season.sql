-- Query 4: Player with most points in a single season
WITH player_season_totals AS (
    SELECT 
        gd.player_name,
        ps.season,
        SUM(gd.pts) AS total_points,
        COUNT(*) AS games_played,
        ROUND(AVG(gd.pts), 2) AS avg_points_per_game
    FROM game_details gd
    LEFT JOIN player_seasons ps ON gd.player_name = ps.player_name
    WHERE ps.season IS NOT NULL
    GROUP BY gd.player_name, ps.season
),
ranked_players AS (
    SELECT 
        player_name,
        season,
        total_points,
        games_played,
        avg_points_per_game,
        RANK() OVER (ORDER BY total_points DESC) AS points_rank
    FROM player_season_totals
)
SELECT 
    player_name,
    season,
    total_points,
    games_played,
    avg_points_per_game
FROM ranked_players
WHERE points_rank = 1;
