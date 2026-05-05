-- Query 3: Player with most points for a single team
WITH player_team_totals AS (
    SELECT 
        player_name,
        team_abbreviation,
        SUM(pts) AS total_points,
        COUNT(*) AS games_played,
        ROUND(AVG(pts), 2) AS avg_points_per_game
    FROM game_details
    GROUP BY player_name, team_abbreviation
),
ranked_players AS (
    SELECT 
        player_name,
        team_abbreviation,
        total_points,
        games_played,
        avg_points_per_game,
        RANK() OVER (ORDER BY total_points DESC) AS points_rank
    FROM player_team_totals
)
SELECT 
    player_name,
    team_abbreviation,
    total_points,
    games_played,
    avg_points_per_game
FROM ranked_players
WHERE points_rank = 1;
