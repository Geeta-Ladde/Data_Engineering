-- Query 2: GROUPING SETS Aggregations
WITH team_game_scores AS (
    SELECT 
        gd.game_id,
        gd.team_id,
        gd.team_abbreviation,
        SUM(gd.pts) AS team_score
    FROM game_details gd
    GROUP BY gd.game_id, gd.team_id, gd.team_abbreviation
),
game_winners AS (
    SELECT 
        game_id,
        team_id,
        team_abbreviation,
        team_score,
        RANK() OVER (PARTITION BY game_id ORDER BY team_score DESC) AS rnk
    FROM team_game_scores
),
enriched_details AS (
    SELECT 
        gd.player_name,
        gd.team_abbreviation,
        ps.season,
        gd.game_id,
        gd.pts,
        gd.reb,
        gd.ast,
        CASE WHEN gw.rnk = 1 THEN TRUE ELSE FALSE END AS team_won
    FROM game_details gd
    JOIN game_winners gw ON gd.game_id = gw.game_id AND gd.team_id = gw.team_id
    LEFT JOIN player_seasons ps ON gd.player_name = ps.player_name
)
SELECT 
    player_name,
    team_abbreviation,
    season,
    CASE 
        WHEN GROUPING(player_name) = 1 THEN COUNT(DISTINCT game_id)
        ELSE COUNT(*)
    END AS games_played,
    SUM(pts) AS total_points,
    CASE 
        WHEN GROUPING(player_name) = 1 
        THEN ROUND(SUM(pts)::NUMERIC / NULLIF(COUNT(DISTINCT game_id), 0), 2)
        ELSE ROUND(AVG(pts), 2)
    END AS avg_points_per_game,
    COUNT(DISTINCT game_id) FILTER (WHERE team_won = TRUE) AS games_won,
    SUM(reb) AS total_rebounds,
    SUM(ast) AS total_assists
FROM enriched_details
GROUP BY GROUPING SETS (
    (player_name, team_abbreviation),
    (player_name, season),
    (team_abbreviation)
);
