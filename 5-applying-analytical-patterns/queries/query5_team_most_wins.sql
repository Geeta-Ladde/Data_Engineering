-- Query 5: Team with the most total wins
WITH team_game_scores AS (
    SELECT 
        game_id,
        team_id,
        team_abbreviation,
        SUM(pts) AS team_score
    FROM game_details
    GROUP BY game_id, team_id, team_abbreviation
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
team_win_totals AS (
    SELECT 
        team_abbreviation,
        SUM(CASE WHEN rnk = 1 THEN 1 ELSE 0 END) AS total_wins,
        COUNT(*) AS games_played,
        ROUND(SUM(CASE WHEN rnk = 1 THEN 1 ELSE 0 END)::NUMERIC / COUNT(*), 3) AS win_percentage
    FROM game_winners
    GROUP BY team_abbreviation
),
ranked_teams AS (
    SELECT 
        team_abbreviation,
        total_wins,
        games_played,
        win_percentage,
        RANK() OVER (ORDER BY total_wins DESC) AS win_rank
    FROM team_win_totals
)
SELECT 
    team_abbreviation,
    total_wins,
    games_played,
    win_percentage
FROM ranked_teams
WHERE win_rank = 1;
