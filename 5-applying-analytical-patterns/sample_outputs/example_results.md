# 📊 Sample Query Results — NBA Analytical Patterns

---

## Query 1 — Player State Change Tracking

| player_name | season | player_state |
|-------------|--------|-------------|
| LeBron James | 2003 | New |
| LeBron James | 2004 | Continued Playing |
| LeBron James | 2005 | Continued Playing |
| Kobe Bryant | 2016 | Continued Playing |
| Kobe Bryant | 2017 | Retired |
| Kobe Bryant | 2018 | Stayed Retired |
| Retired Player | 2010 | New |
| Retired Player | 2019 | Continued Playing |
| Retired Player | 2020 | Retired |
| Retired Player | 2021 | Stayed Retired |

**State categories explained:**
- `New` — First season in the league
- `Continued Playing` — Active last season and this season
- `Retired` — Was active last season, inactive this season
- `Stayed Retired` — Inactive last season and this season
- `Returned from Retirement` — Was inactive, now active again

---

## Query 2 — GROUPING SETS Multi-Dimensional Aggregations

### Grouping 1: Player + Team
| player_name | team_abbreviation | season | games_played | total_points | avg_ppg | games_won |
|-------------|------------------|--------|-------------|-------------|---------|-----------|
| LeBron James | LAL | NULL | 7 | 138 | 19.7 | 4 |
| Stephen Curry | GSW | NULL | 5 | 165 | 33.0 | 3 |
| Jayson Tatum | BOS | NULL | 4 | 100 | 25.0 | 2 |

### Grouping 2: Player + Season
| player_name | team_abbreviation | season | games_played | total_points | avg_ppg |
|-------------|------------------|--------|-------------|-------------|---------|
| LeBron James | NULL | 2021 | 4 | 85 | 21.3 |
| LeBron James | NULL | 2022 | 3 | 53 | 17.7 |
| Stephen Curry | NULL | 2021 | 3 | 106 | 35.3 |

### Grouping 3: Team Only
| player_name | team_abbreviation | season | total_points | avg_ppg |
|-------------|------------------|--------|-------------|---------|
| NULL | LAL | NULL | 182 | 26.0 |
| NULL | GSW | NULL | 186 | 37.2 |
| NULL | BOS | NULL | 124 | 31.0 |

> **Power of GROUPING SETS:** One query returns three different
> aggregation levels simultaneously — no UNION needed.

---

## Query 3 — Player with Most Points for a Single Team

| player_name | team_abbreviation | total_points | games_played | avg_ppg |
|-------------|------------------|-------------|-------------|---------|
| Stephen Curry | GSW | 165 | 5 | 33.0 |

> Stephen Curry scored the most total points while playing for GSW.

---

## Query 4 — Player with Most Points in a Single Season

| player_name | season | total_points | games_played | avg_ppg |
|-------------|--------|-------------|-------------|---------|
| Stephen Curry | 2021 | 106 | 3 | 35.3 |

> Stephen Curry's 2021 season had the highest total points scored.

---

## Query 5 — Team with Most Total Wins

| team_abbreviation | total_wins | games_played | win_percentage |
|------------------|-----------|-------------|----------------|
| LAL | 4 | 7 | 0.571 |

---

## Query 6 — Best 90-Game Stretch (Rolling Window)

| team_abbreviation | max_wins_in_90_games |
|------------------|---------------------|
| GSW | 73 |

> Using a **rolling 90-game window** (`ROWS BETWEEN 89 PRECEDING AND CURRENT ROW`)
> to find the best consecutive stretch for any team in history.

---

## Query 7 — LeBron James Longest Scoring Streak (10+ Points)

| player_name | longest_streak | streak_start_game | streak_end_game | min_pts | max_pts | avg_pts |
|-------------|---------------|------------------|-----------------|---------|---------|---------|
| LeBron James | 6 | game_001 | game_006 | 12 | 33 | 23.0 |

**How gap-and-island streak detection works:**
```
Game | pts | 10+? | running_sum | game_num | group (game_num - running_sum)
-----|-----|------|------------|----------|-------------------------------
  1  |  28 |  1   |     1      |    1     |  0  ← group 0 starts
  2  |  32 |  1   |     2      |    2     |  0
  3  |  12 |  1   |     3      |    3     |  0
  4  |   8 |  0   |     3      |    4     |  1  ← not in streak
  5  |  25 |  1   |     4      |    5     |  1  ← group 1 starts
  6  |  33 |  1   |     5      |    6     |  1
```
> Rows with the same `group` value form a consecutive streak.
> The longest streak = the group with the most rows.

---

## Key SQL Techniques Summary

| Query | Technique | Complexity |
|-------|-----------|------------|
| Q1 | LAG() + CROSS JOIN + GENERATE_SERIES | ⭐⭐⭐⭐ |
| Q2 | GROUPING SETS across 3 dimensions | ⭐⭐⭐⭐⭐ |
| Q3 | RANK() for tie handling | ⭐⭐⭐ |
| Q4 | Multi-table join + RANK() | ⭐⭐⭐ |
| Q5 | Window RANK() for game winners | ⭐⭐⭐⭐ |
| Q6 | Rolling window ROWS BETWEEN 89 PRECEDING | ⭐⭐⭐⭐⭐ |
| Q7 | Gap-and-island streak detection | ⭐⭐⭐⭐⭐ |
