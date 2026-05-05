# 🏀 Advanced NBA Analytics — SQL Analytical Patterns

> **Seven production-grade SQL queries demonstrating advanced analytical
> patterns including GROUPING SETS, rolling window aggregations,
> gap-and-island streak detection, and multi-dimensional state tracking
> on NBA game and player data.**

---

## 📌 Project Summary

This project applies advanced SQL analytical patterns to NBA game statistics,
answering real business intelligence questions that require sophisticated
window functions, multi-level aggregations, and temporal state tracking.

**The business questions answered:**
> - *"How has each player's active status changed season over season?"*
> - *"What are the scoring totals across player, team, and season dimensions simultaneously?"*
> - *"Which team had the best 90-game winning stretch in history?"*
> - *"What is LeBron James's longest consecutive 10+ point scoring streak?"*

---

## 🏗️ Data Model

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────┐
│  game_details   │     │  player_seasons  │     │  players_scd  │
│                 │     │                  │     │               │
│  game_id        │     │  player_name     │     │  player_name  │
│  team_id        │     │  season          │     │  is_active    │
│  team_abbr      │     │  pts             │     │  start_season │
│  player_name    │     │  ast             │     │  end_season   │
│  pts            │     │  reb             │     │  scoring_class│
│  reb            │     │  weight          │     │               │
│  ast            │     └──────────────────┘     └───────────────┘
└─────────────────┘
```

---

## 📁 Repository Structure

```
05_analytical_patterns/
│
├── README.md
│
├── queries/
│   ├── query1_player_state_changes.sql       ← Season-over-season state tracking
│   ├── query2_grouping_sets_aggregations.sql ← Multi-dimensional GROUPING SETS
│   ├── query3_most_points_per_team.sql       ← Top scorer per team
│   ├── query4_most_points_per_season.sql     ← Top scorer per season
│   ├── query5_team_most_wins.sql             ← Team win totals + percentage
│   ├── query6_best_90_game_stretch.sql       ← Rolling 90-game window
│   └── query7_lebron_scoring_streak.sql      ← Gap-and-island streak detection
│
├── sample_data/
│   └── nba_sample_data.sql                   ← Sample data to run queries against
│
└── sample_outputs/
    └── example_results.md                    ← Sample results with explanations
```

---

## 🛠️ Tech Stack

| Technology | Usage |
|------------|-------|
| **PostgreSQL 14+** | Primary query engine |
| **GROUPING SETS** | Multi-dimensional aggregations |
| **Window Functions** | LAG, RANK, ROW_NUMBER, SUM OVER |
| **Rolling Windows** | ROWS BETWEEN N PRECEDING AND CURRENT ROW |
| **Gap-and-Island** | Consecutive streak detection pattern |
| **GENERATE_SERIES** | Dynamic season spine generation |
| **CTEs** | Modular, readable query composition |

---

## 💡 Key Patterns Demonstrated

### Pattern 1 — Season-over-Season State Change Tracking
Generates a complete season spine using `GENERATE_SERIES` and
`CROSS JOIN`, then uses `LAG()` to detect transitions between
active and inactive states for every player.

```sql
-- Generate all seasons × all players combinations
player_season_grid AS (
    SELECT p.player_name, s.season
    FROM player_list p
    CROSS JOIN season_spine s
),
-- Detect state transitions using LAG
lagged_activity AS (
    SELECT
        player_name, season, is_active,
        LAG(is_active) OVER (
            PARTITION BY player_name ORDER BY season
        ) AS prev_is_active
    FROM player_activity
)
-- Classify each transition
CASE
    WHEN prev_is_active IS NULL AND is_active = TRUE  THEN 'New'
    WHEN prev_is_active = TRUE  AND is_active = FALSE THEN 'Retired'
    WHEN prev_is_active = TRUE  AND is_active = TRUE  THEN 'Continued Playing'
    WHEN prev_is_active = FALSE AND is_active = TRUE  THEN 'Returned from Retirement'
    WHEN prev_is_active = FALSE AND is_active = FALSE THEN 'Stayed Retired'
END AS player_state
```

### Pattern 2 — GROUPING SETS Multi-Dimensional Aggregation
Returns three aggregation levels in a single query pass — by
player+team, player+season, and team only — far more efficient
than three separate queries or UNION ALL.

```sql
GROUP BY GROUPING SETS (
    (player_name, team_abbreviation),  -- Level 1: per player per team
    (player_name, season),             -- Level 2: per player per season
    (team_abbreviation)                -- Level 3: per team only
)
```

### Pattern 3 — Rolling Window Aggregation (90-game stretch)
Uses a bounded window frame to calculate the maximum wins in
any consecutive 90-game stretch for each team.

```sql
SUM(is_win) OVER (
    PARTITION BY team_id
    ORDER BY game_number
    ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
) AS wins_in_90_games
```

### Pattern 4 — Gap-and-Island Streak Detection
Classic advanced SQL pattern for finding consecutive sequences.
Subtracting a cumulative count from row number creates identical
values for consecutive rows — grouping them into "islands."

```sql
-- The gap-and-island key insight:
game_number - SUM(CASE WHEN scored_10_plus = 1 THEN 1 ELSE 0 END)
              OVER (PARTITION BY player_name ORDER BY game_id
                   ROWS UNBOUNDED PRECEDING) AS streak_group
-- Rows in the same streak share the same streak_group value
```

### Pattern 5 — RANK() for Tie-Safe Results
All ranking queries use `RANK()` instead of `LIMIT 1` to correctly
handle tied results — returning all players/teams that share the top position.

```sql
RANK() OVER (ORDER BY total_points DESC) AS points_rank
-- WHERE points_rank = 1 returns ALL players tied for first
```

---

## 📊 Sample Results

See [sample_outputs/example_results.md](sample_outputs/example_results.md)
for full query outputs. Quick preview:

### Query 1 — State Changes
| player_name | season | player_state |
|-------------|--------|-------------|
| LeBron James | 2003 | New |
| LeBron James | 2004 | Continued Playing |
| Kobe Bryant | 2017 | Retired |

### Query 2 — GROUPING SETS
| player_name | team | season | total_pts | avg_ppg |
|-------------|------|--------|-----------|---------|
| LeBron James | LAL | NULL | 138 | 19.7 |
| LeBron James | NULL | 2022 | 53 | 17.7 |
| NULL | LAL | NULL | 182 | 26.0 |

### Query 7 — LeBron's Longest Streak
| player_name | longest_streak | min_pts | max_pts | avg_pts |
|-------------|---------------|---------|---------|---------|
| LeBron James | 6 games | 12 | 33 | 23.0 |

---

## 🚀 How to Run

### Prerequisites
- PostgreSQL 12+ installed
- NBA game dataset loaded

### Step 1 — Load sample data
```bash
psql -d your_database -f sample_data/nba_sample_data.sql
```

### Step 2 — Run queries individually
```bash
psql -d your_database -f queries/query1_player_state_changes.sql
psql -d your_database -f queries/query2_grouping_sets_aggregations.sql
psql -d your_database -f queries/query3_most_points_per_team.sql
psql -d your_database -f queries/query4_most_points_per_season.sql
psql -d your_database -f queries/query5_team_most_wins.sql
psql -d your_database -f queries/query6_best_90_game_stretch.sql
psql -d your_database -f queries/query7_lebron_scoring_streak.sql
```

### Recommended execution order
```
1 → 2 → 3 → 4 → 5 → 6 → 7
(State tracking) → (Aggregations) → (Rankings) → (Streaks)
```

---

## 💼 Real-World Applications

| Pattern | Industry Application |
|---------|---------------------|
| State change tracking | Customer churn analysis, subscription tracking |
| GROUPING SETS | Executive dashboards with drill-down capability |
| Rolling windows | Financial moving averages, fraud detection |
| Gap-and-island | Uptime streaks, consecutive login tracking |
| RANK() for ties | Leaderboards, fair competition ranking |

---

## 🎓 About This Project

This project demonstrates production-ready analytical SQL patterns
applied to NBA game data — implementing the advanced aggregation,
window function, and temporal tracking techniques used in modern
business intelligence and data analytics platforms.

---

## 👩‍💻 Author

**Geeta Bhushan Ladde**
Senior Data and Quality Engineer

- 🔗 [LinkedIn](https://www.linkedin.com/in/geetasa/)
- 📧 geetas0915@gmail.com
- 📍 Folsom, CA

---

## 📚 Further Reading

- [PostgreSQL Window Functions](https://www.postgresql.org/docs/current/tutorial-window.html)
- [GROUPING SETS Documentation](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-GROUPING-SETS)
- [Gap and Island Problems — SQL Patterns](https://www.sqlservercentral.com/articles/the-gaps-and-islands-of-sequential-series)

---

⭐ **If this helped you understand advanced SQL patterns, please give it a star!**
