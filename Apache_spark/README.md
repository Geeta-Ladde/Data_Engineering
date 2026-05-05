# ⚡ Apache Spark — PySpark ETL Jobs with Unit Testing

> **Production-grade PySpark jobs implementing SCD Type 2, cumulative season
> arrays, and Halo 5 gaming analytics — with full pytest unit test coverage
> across 12 test cases.**

---

## 📌 Project Summary

This project contains three production-ready PySpark jobs that demonstrate
core data engineering patterns used at scale. Each job is built with explicit
schemas, parameterized inputs, and a corresponding pytest test suite — the
same standard expected in professional data engineering teams.

**What this project covers:**
> - *Migrating PostgreSQL SCD Type 2 logic into scalable PySpark jobs*
> - *Building cumulative player season arrays incrementally year over year*
> - *Comparing Spark join strategies — broadcast, bucket, and sort-based joins*
> - *Validating pipeline correctness with 12 pytest unit tests*

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                         │
│   players_scd.parquet   player_seasons.parquet   CSV files  │
└──────────┬──────────────────┬──────────────────────────────┘
           │                  │
  ┌────────▼────────┐  ┌──────▼──────────────┐  ┌───────────────────┐
  │   JOB 1         │  │   JOB 2             │  │   JOB 3           │
  │ Incremental     │  │ Cumulative          │  │ Gaming Analysis   │
  │ SCD Type 2      │  │ Players             │  │ Halo 5 Dataset    │
  │                 │  │                     │  │                   │
  │ Tracks player   │  │ Accumulates         │  │ Broadcast joins   │
  │ quality changes │  │ season stats        │  │ Bucket joins      │
  │ over time       │  │ into arrays         │  │ Partitioning      │
  └────────┬────────┘  └──────┬──────────────┘  └───────┬───────────┘
           │                  │                          │
  ┌────────▼──────────────────▼──────────────────────────▼───────────┐
  │                        PYTEST TEST SUITE                         │
  │   test_incremental_scd_job.py    (7 tests + end-to-end)          │
  │   test_cumulative_players_job.py (5 tests + end-to-end)          │
  │   test_gaming_analysis_job.py    (smoke tests)                   │
  └──────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
03_apache_spark/
│
├── README.md
├── requirements.txt
│
├── jobs/
│   ├── incremental_scd_job.py         ← SCD Type 2 PySpark job
│   ├── cumulative_players_job.py      ← Cumulative season arrays job
│   └── gaming_analysis_job.py         ← Halo 5 gaming analytics job
│
├── tests/
│   ├── test_incremental_scd_job.py    ← 7 pytest tests for SCD job
│   ├── test_cumulative_players_job.py ← 5 pytest tests for cumulative job
│   └── test_gaming_analysis_job.py    ← Smoke tests for gaming job
│
├── data/
│   ├── matches.csv                    ← Halo 5 match records
│   ├── match_details.csv              ← Player stats per match
│   ├── medals.csv                     ← Medal definitions
│   ├── maps.csv                       ← Map metadata
│   ├── medals_matches_players.csv     ← Medal awards per match
│   ├── devices.csv                    ← Device metadata
│   └── events.csv                     ← Web event logs
│
└── sample_outputs/
    └── example_results.md             ← Sample job outputs & test results
```

---

## 🛠️ Tech Stack

| Technology | Usage |
|------------|-------|
| **PySpark 3.3+** | Distributed data processing engine |
| **SparkSQL** | SQL-based transformations within Spark |
| **pytest** | Unit and integration testing framework |
| **Parquet** | Columnar storage format for job I/O |
| **StructType Schemas** | Explicit schema enforcement |
| **Broadcast Join** | Optimized join for small lookup tables |
| **Bucket Join** | Shuffle-free join for large tables |
| **Null-safe equality (`<=>`)** | Safe comparisons with NULL values |

---

## 💡 Key Patterns Demonstrated

### Pattern 1 — SCD Type 2 with Null-Safe Comparisons
Tracks player quality class changes year over year, handling NULL values
safely using Spark's null-safe equality operator `<=>`.

```python
# Null-safe equality prevents incorrect change detection on NULL fields
WHERE (ts.scoring_class <=> ls.scoring_class)
AND   (ts.is_active     <=> ls.is_active)

# Change detection — opens new record, closes old one
changed_records_old AS (
    SELECT ls.*, ls.end_season          -- Close old record
    FROM last_season_scd ls
    JOIN this_season_data ts ON ls.player_name = ts.player_name
    WHERE NOT (ts.scoring_class <=> ls.scoring_class)
),
changed_records_new AS (
    SELECT ts.*, current_season AS start_season  -- Open new record
    ...
)
```

### Pattern 2 — Cumulative Array Accumulation
Appends each season's stats to a growing array — never reprocessing
historical data, only adding the new season incrementally.

```python
# Carry forward existing seasons + append new season
CASE
    WHEN ls.seasons IS NOT NULL THEN
        array_union(
            ls.seasons,
            array(struct(ts.season, ts.pts, ts.ast, ts.reb, ts.weight))
        )
    ELSE
        array(struct(ts.season, ts.pts, ts.ast, ts.reb, ts.weight))
END AS seasons
```

### Pattern 3 — Broadcast vs Bucket Join Comparison
Demonstrates three join strategies and when to use each in production.

```python
# Strategy 1 — Broadcast join (small lookup tables < 200MB)
medals_broadcast = F.broadcast(tables["medals"])
df.join(medals_broadcast, "medal_id", "left")

# Strategy 2 — Bucket join (eliminates shuffle for large tables)
tables["match_details"].write \
    .bucketBy(16, "match_id") \
    .sortBy("match_id") \
    .saveAsTable("md_bucketed")

# Strategy 3 — No broadcast (baseline comparison)
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
```

### Pattern 4 — Partitioning with sortWithinPartitions
Compares three partitioning strategies and measures output size
to determine the optimal layout for downstream queries.

```python
# Partition by single key
aggregated_df.repartition("playlist_id") \
    .sortWithinPartitions("playlist_id") \
    .write.partitionBy("playlist_id") \
    .parquet("output/part_by_playlist")

# Partition by composite key
aggregated_df.repartition("playlist_id", "mapid") \
    .sortWithinPartitions("playlist_id", "mapid") \
    .write.partitionBy("playlist_id", "mapid") \
    .parquet("output/part_by_playlist_map")
```

### Pattern 5 — Explicit Schema Definition
All jobs define explicit StructType schemas rather than relying on
schema inference — essential for production reliability.

```python
season_stats_schema = StructType([
    StructField("season",  IntegerType(), True),
    StructField("pts",     FloatType(),   True),
    StructField("ast",     FloatType(),   True),
    StructField("reb",     FloatType(),   True),
    StructField("weight",  FloatType(),   True)
])
```

---

## 🧪 Test Coverage

This project includes **12 pytest tests** covering real edge cases —
the same scenarios that cause production pipelines to fail silently.

### TestIncrementalSCDJob — 7 Tests

| Test | Scenario Covered |
|------|-----------------|
| `test_unchanged_players_extend_season` | end_season correctly extended |
| `test_changed_players_create_new_records` | Old record closed, new record opened |
| `test_new_players_get_initial_records` | First-time player insert |
| `test_historical_records_preserved` | Old closed records untouched |
| `test_dropped_players_preserved` | Players who retire mid-season |
| `test_null_safe_comparisons` | NULL scoring_class handled correctly |
| `test_scd_job_end_to_end` | Full file I/O pipeline (Parquet in → Parquet out) |

### TestCumulativePlayersJob — 5 Tests

| Test | Scenario Covered |
|------|-----------------|
| `test_new_player_first_season` | First season array initialized |
| `test_existing_player_no_new_season` | Inactive player preserved correctly |
| `test_scoring_class_calculation` | All 4 tiers (star/good/average/bad) |
| `test_existing_player_adds_new_season` | Season appended to existing array |
| `test_cumulative_job_end_to_end` | Full file I/O pipeline (Parquet in → Parquet out) |

---

## 🚀 How to Run

### Prerequisites
```bash
pip install -r requirements.txt
# Requires Java 8 or 11 for PySpark
```

### Run Individual Jobs

**Incremental SCD Job:**
```bash
spark-submit jobs/incremental_scd_job.py \
  --last_scd_path data/players_scd.parquet \
  --current_season_path data/players_2022.parquet \
  --output_path output/players_scd_updated.parquet \
  --previous_season 2021 \
  --current_season 2022
```

**Cumulative Players Job:**
```bash
spark-submit jobs/cumulative_players_job.py \
  --last_season_path data/players_1997.parquet \
  --current_season_path data/player_seasons_1998.parquet \
  --output_path output/players_1998.parquet \
  --target_season 1998
```

**Gaming Analysis Job:**
```bash
spark-submit jobs/gaming_analysis_job.py
# Uses data/ folder automatically
```

### Run All Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test class
pytest tests/test_incremental_scd_job.py -v

# Run with coverage report
pytest tests/ -v --cov=jobs --cov-report=term-missing
```

**Expected test output:**
```
tests/test_incremental_scd_job.py::TestIncrementalSCDJob::test_unchanged_players_extend_season PASSED
tests/test_incremental_scd_job.py::TestIncrementalSCDJob::test_changed_players_create_new_records PASSED
tests/test_incremental_scd_job.py::TestIncrementalSCDJob::test_new_players_get_initial_records PASSED
tests/test_incremental_scd_job.py::TestIncrementalSCDJob::test_historical_records_preserved PASSED
tests/test_incremental_scd_job.py::TestIncrementalSCDJob::test_dropped_players_preserved PASSED
tests/test_incremental_scd_job.py::TestIncrementalSCDJob::test_null_safe_comparisons PASSED
tests/test_incremental_scd_job.py::TestIncrementalSCDJob::test_scd_job_end_to_end PASSED
tests/test_cumulative_players_job.py::TestCumulativePlayersJob::test_new_player_first_season PASSED
tests/test_cumulative_players_job.py::TestCumulativePlayersJob::test_existing_player_no_new_season PASSED
tests/test_cumulative_players_job.py::TestCumulativePlayersJob::test_scoring_class_calculation PASSED
tests/test_cumulative_players_job.py::TestCumulativePlayersJob::test_existing_player_adds_new_season PASSED
tests/test_cumulative_players_job.py::TestCumulativePlayersJob::test_cumulative_job_end_to_end PASSED
12 passed in 45.32s
```

---

## 📊 Sample Results

See [sample_outputs/example_results.md](sample_outputs/example_results.md)
for full job outputs. Quick preview:

### SCD Type 2 — Change Detection Output
| player_name | scoring_class | start_season | end_season | status |
|-------------|---------------|--------------|------------|--------|
| LeBron James | star | 2018 | 2022 | ✅ Extended |
| Steph Curry | star | 2020 | 2021 | ✅ Closed |
| Steph Curry | good | 2022 | 2022 | ✅ New record |
| Rookie Smith | average | 2022 | 2022 | ✅ First insert |

### Join Strategy Comparison
| Strategy | Shuffle Required | Best For |
|----------|-----------------|----------|
| Broadcast join | No (small table) | Medals, Maps lookup |
| Bucket join | No (pre-bucketed) | Large match tables |
| Sort-based join | Yes | Ad-hoc queries |

---

## 💼 Real-World Applications

| Pattern | Industry Use Case |
|---------|-----------------|
| SCD Type 2 | Customer status tracking, subscription changes |
| Cumulative Arrays | User activity history, session accumulation |
| Broadcast Join | Dimension table lookups in data warehouses |
| Bucket Join | Large fact table joins in data lakes |
| Partitioning Strategy | Optimizing Athena/Redshift Spectrum query costs |

---

## 🎓 About This Project

This project demonstrates production-ready PySpark patterns applied to
NBA player data and Halo 5 gaming analytics — implementing the distributed
processing, join optimization, and test-driven development practices used
in modern data engineering teams.

---

## 👩‍💻 Author

**Geeta Bhushan Ladde**
Senior Data and Quality Engineer

- 🔗 [LinkedIn](https://www.linkedin.com/in/geetasa/)
- 📧 geetas0915@gmail.com
- 📍 Folsom, CA

---

## 📚 Further Reading

- [PySpark Documentation](https://spark.apache.org/docs/latest/api/python/)
- [Spark Optimization Guide](https://spark.apache.org/docs/latest/tuning.html)
- [pytest Documentation](https://docs.pytest.org/)

---

⭐ **If this helped you understand PySpark testing patterns, please give it a star!**
