# 📊 Sample Job Outputs

---

## Job 1 — Incremental SCD Type 2 (Players)

### Input: players_scd (2021 snapshot)
| player_name | scoring_class | is_active | start_season | end_season |
|-------------|---------------|-----------|--------------|------------|
| LeBron James | star | true | 2018 | 2021 |
| Steph Curry | star | true | 2020 | 2021 |
| Retired Player | good | false | 2015 | 2019 |

### Input: players (2022 season)
| player_name | scoring_class | is_active | current_season |
|-------------|---------------|-----------|----------------|
| LeBron James | star | true | 2022 |
| Steph Curry | good | true | 2022 |
| Rookie Smith | average | true | 2022 |

### Output: players_scd (2022 snapshot)
| player_name | scoring_class | is_active | start_season | end_season | current_season |
|-------------|---------------|-----------|--------------|------------|----------------|
| Retired Player | good | false | 2015 | 2019 | 2022 |
| LeBron James | star | true | 2018 | 2022 | 2022 |
| Steph Curry | star | true | 2020 | 2021 | 2022 |
| Steph Curry | good | true | 2022 | 2022 | 2022 |
| Rookie Smith | average | true | 2022 | 2022 | 2022 |

**What happened:**
- LeBron — unchanged → `end_season` extended from 2021 to 2022
- Steph Curry — changed scoring class → old record closed at 2021, new record opened at 2022
- Retired Player — historical record preserved untouched
- Rookie Smith — brand new player, inserted with start/end = 2022

---

## Job 2 — Cumulative Players (Season Array Accumulation)

### Input: players (1997 snapshot)
| player_name | seasons | scoring_class | is_active | current_season |
|-------------|---------|---------------|-----------|----------------|
| Michael Jordan | [{1996: pts=30.1, ast=4.3, reb=6.6}] | star | true | 1997 |

### Input: player_seasons (1998)
| player_name | season | pts | ast | reb |
|-------------|--------|-----|-----|-----|
| Michael Jordan | 1998 | 28.7 | 3.5 | 5.8 |
| Kobe Bryant | 1998 | 7.6 | 1.3 | 1.9 |

### Output: players (1998 snapshot)
| player_name | seasons | scoring_class | is_active | current_season |
|-------------|---------|---------------|-----------|----------------|
| Michael Jordan | [{1996: pts=30.1}, {1998: pts=28.7}] | star | true | 1998 |
| Kobe Bryant | [{1998: pts=7.6}] | bad | true | 1998 |

**What happened:**
- Jordan — 1998 season appended to existing array, scoring class recalculated (28.7 > 20 = star)
- Kobe — first season, new array created (7.6 pts = bad class — he was a rookie!)

---

## Job 3 — Gaming Analysis (Halo 5 Dataset)

### Query 4a — Top Players by Average Kills
| player_gamertag | avg_kills_per_game | games_played |
|-----------------|-------------------|--------------|
| EcZachly | 18.4 | 847 |
| Player2 | 16.2 | 623 |
| Player3 | 15.9 | 412 |

### Query 4b — Most Played Playlists
| playlist_id | plays |
|-------------|-------|
| playlist_abc | 12847 |
| playlist_def | 9234 |
| playlist_ghi | 7891 |

### Query 4c — Most Played Maps
| map_name | times_played |
|----------|-------------|
| Urban | 8943 |
| Raid on Apex 7 | 7234 |
| Truth | 6891 |

### Query 4d — Killing Spree Medals by Map
| map_name | killing_spree_medals |
|----------|---------------------|
| Urban | 2341 |
| Empire | 1987 |
| Regret | 1654 |

---

## Join Strategy Performance Comparison (Query 5)

| Strategy | Output Size | Use When |
|----------|-------------|----------|
| No Broadcast Join | Largest | Never for small tables |
| Broadcast Join | Medium | Small lookup tables < 200MB |
| Bucket Join | Smallest | Large tables joined repeatedly |

**Key insight:** Bucket joins eliminate shuffle completely for large-to-large
joins on the same key, making them **3-5x faster** than regular joins at scale.

### Partitioning Strategy Comparison
| Strategy | Best For | Query Pattern |
|----------|----------|---------------|
| Partition by playlist_id | Playlist analytics | Filter by playlist |
| Partition by mapid | Map analytics | Filter by map |
| Partition by playlist + map | Mixed analytics | Filter by both |

---

## Test Coverage Summary

### TestIncrementalSCDJob (7 tests)
| Test | What It Verifies |
|------|-----------------|
| test_unchanged_players_extend_season | end_season updated correctly |
| test_changed_players_create_new_records | 2 records created on change |
| test_new_players_get_initial_records | First-time inserts work |
| test_historical_records_preserved | Old records not touched |
| test_dropped_players_preserved | Retired players handled |
| test_null_safe_comparisons | NULL scoring_class handled |
| test_scd_job_end_to_end | Full file I/O pipeline works |

### TestCumulativePlayersJob (5 tests)
| Test | What It Verifies |
|------|-----------------|
| test_new_player_first_season | First season array created |
| test_existing_player_no_new_season | Inactive player preserved |
| test_scoring_class_calculation | All 4 tiers calculated correctly |
| test_existing_player_adds_new_season | Season appended to array |
| test_cumulative_job_end_to_end | Full file I/O pipeline works |
