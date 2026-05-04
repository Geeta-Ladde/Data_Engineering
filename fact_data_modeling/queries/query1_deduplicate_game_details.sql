-- Query 1: Deduplicate game_details from Day 1
-- This query removes duplicate records from the game_details table

SELECT 
    game_id,
    team_id,
    team_abbreviation,
    team_city,
    player_id,
    player_name,
    nickname,
    start_position,
    comment,
    min,
    fgm,
    fga,
    fg_pct,
    fg3m,
    fg3a,
    fg3_pct,
    ftm,
    fta,
    ft_pct,
    oreb,
    dreb,
    reb,
    ast,
    stl,
    blk,
    to_,
    pf,
    pts,
    plus_minus
FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY game_id, team_id, player_id 
               ORDER BY game_id
           ) AS row_num
    FROM game_details
) deduped
WHERE row_num = 1;
