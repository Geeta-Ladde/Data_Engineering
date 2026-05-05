-- Query 6: Most games won by a team in a 90-game stretch
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
        RANK() OVER (PARTITION BY game_id ORDER BY team_score DESC) AS rnk
    FROM team_game_scores
),
team_games_ordered AS (
    SELECT 
        team_id,
        team_abbreviation,
        game_id,
        CASE WHEN rnk = 1 THEN 1 ELSE 0 END AS is_win,
        ROW_NUMBER() OVER (PARTITION BY team_id ORDER BY game_id) AS game_number
    FROM game_winners
),
rolling_wins AS (
    SELECT 
        team_id,
        team_abbreviation,
        game_number,
        SUM(is_win) OVER (
            PARTITION BY team_id 
            ORDER BY game_number 
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS wins_in_90_games,
        COUNT(*) OVER (
            PARTITION BY team_id 
            ORDER BY game_number 
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS games_in_window
    FROM team_games_ordered
),
max_wins_per_team AS (
    SELECT 
        team_abbreviation,
        MAX(wins_in_90_games) AS max_wins_in_90_games
    FROM rolling_wins
    WHERE games_in_window = 90
    GROUP BY team_abbreviation
),
ranked_teams AS (
    SELECT 
        team_abbreviation,
        max_wins_in_90_games,
        RANK() OVER (ORDER BY max_wins_in_90_games DESC) AS win_rank
    FROM max_wins_per_team
)
SELECT 
    team_abbreviation,
    max_wins_in_90_games
FROM ranked_teams
WHERE win_rank = 1;
