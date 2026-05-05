# 📡 Fact Data Modeling — Web Activity & NBA Game Analytics

> **Production-grade Trino/Presto SQL implementing cumulative fact tables,
> bitmap activity tracking, reduced monthly aggregations, and deduplication
> patterns across web events and NBA game datasets.**

---

## 📌 Project Summary

This project builds a complete **fact data modeling pipeline** that tracks user
web activity across devices and hosts over time. It demonstrates the advanced
patterns used in production data warehouses to handle high-volume event data
efficiently.

**The business questions answered:**
> - *"Which browsers and devices is each user active on, and on which days?"*
> - *"Which hosts are experiencing activity, and when?"*
> - *"How can we store 30 days of daily metrics in a single row per host?"*
> - *"How do we remove duplicate records from raw game data?"*

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SOURCE TABLES                            │
│  nba_game_details (raw)   web_events (raw)   devices (lookup)   │
└──────────┬───────────────────────┬───────────────────────────────┘
           │                       │
  ┌────────▼────────┐   ┌──────────▼──────────────┐
  │  DEDUPLICATED   │   │   CUMULATIVE TABLES      │
  │  game_details   │   │                          │
  │  (Query 1)      │   │  user_devices_cumulated  │
  └─────────────────┘   │  (browser → date array)  │
                        │                          │
                        │  hosts_cumulated         │
                        │  (host → date array)     │
                        └──────────┬───────────────┘
                                   │
                        ┌──────────▼───────────────┐
                        │    DERIVED / REDUCED      │
                        │                          │
                        │  datelist_int            │
                        │  (bitmap encoding)       │
                        │                          │
                        │  host_activity_reduced   │
                        │  (monthly array facts)   │
                        └──────────────────────────┘
```

---

## 📁 Repository Structure

```
02_fact_data_modeling/
│
├── README.md                                        ← You are here
│
├── ddl/
│   ├── query2_user_devices_cumulated_ddl.sql        ← User device tracking table
│   ├── query5_hosts_cumulated_ddl.sql               ← Host activity tracking table
│   └── query7_host_activity_reduced_ddl.sql         ← Monthly reduced fact table
│
├── queries/
│   ├── query1_deduplicate_game_details.sql          ← Remove duplicate NBA records
│   ├── query3_generate_device_activity_datelist.sql ← Cumulative device activity
│   ├── query4_datelist_int_generation.sql           ← Bitmap integer conversion
│   ├── query6_generate_host_activity_datelist.sql   ← Cumulative host activity
│   └── query8_load_host_activity_reduced.sql        ← Monthly incremental load
│
├── sample_data/
│   ├── web_events_sample.csv                        ← 20 rows sample web events
│   ├── devices_sample.csv                           ← 10 rows sample device data
│   └── nba_game_details_sample.csv                  ← Sample game data with dupes
│
└── sample_outputs/
    └── example_results.md                           ← Sample results & explanations
```

---

## 🛠️ Tech Stack

| Technology | Usage |
|------------|-------|
| **Trino / Presto SQL** | Primary query engine |
| **MAP<VARCHAR, ARRAY<DATE>>** | Browser-to-dates activity tracking |
| **ARRAY<BIGINT>** | Monthly metric arrays |
| **Bitmap Integers** | Efficient activity encoding |
| **MERGE statement** | Idempotent incremental loads |
| **ROW_NUMBER()** | Deterministic deduplication |
| **Apache Airflow** | Pipeline orchestration ({{ ds }} templating) |

---

## 💡 Key Patterns Demonstrated

### Pattern 1 — Deduplication with ROW_NUMBER()
Raw event tables often contain duplicate records. This pattern removes them
deterministically without losing any legitimate data.

```sql
SELECT * FROM (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY game_id, team_id, player_id
            ORDER BY game_id, team_id, player_id
        ) AS rn
    FROM nba_game_details
) deduped
WHERE rn = 1;
```

### Pattern 2 — MAP Aggregation for Multi-Dimensional Activity
Instead of one row per user per browser, all browser activity is stored
in a single MAP per user — dramatically reducing cardinality.

```sql
-- Aggregate ALL browser types into one map per user
SELECT
    e.user_id,
    MAP_AGG(
        d.browser_type,
        ARRAY_AGG(DISTINCT DATE(e.event_time))
    ) AS today_map
FROM web_events e
JOIN devices d ON e.device_id = d.device_id
WHERE DATE(e.event_time) = DATE('{{ ds }}')
GROUP BY e.user_id   -- ONE row per user, not per browser!
```

### Pattern 3 — Cumulative Array Building
Each day appends to the historical date array — no reprocessing of old data.

```sql
-- Merge yesterday's history with today's new activity
MAP_CONCAT(
    y.device_activity_datelist,
    TRANSFORM_VALUES(
        t.today_map,
        (k, v) -> ARRAY_UNION(
            COALESCE(y.device_activity_datelist[k], CAST(ARRAY[] AS ARRAY(DATE))),
            COALESCE(v, CAST(ARRAY[] AS ARRAY(DATE)))
        )
    )
) AS device_activity_datelist
```

### Pattern 4 — Bitmap Integer Encoding
Convert date arrays to integers for ultra-fast activity queries using
bitwise operations — each bit represents one day of the month.

```sql
-- Each active day becomes a power of 2
-- Jan 1 = 2^0 = 1, Jan 2 = 2^1 = 2, Jan 3 = 2^2 = 4 ...
CAST(
    SUM(POW(2, DATE_DIFF('day', month_start, activity_date)))
AS BIGINT) AS datelist_int

-- Query: Was user active on Jan 3?
-- datelist_int & POW(2, 2) > 0  →  true/false in microseconds!
```

### Pattern 5 — Reduced Monthly Fact Table with Gap Filling
Store 31 days of metrics in a single array row per host, filling
missing days with zeros automatically.

```sql
-- MERGE handles both new months and daily updates
MERGE INTO host_activity_reduced t
USING (...) s
ON t.host = s.host AND t.month = s.month
WHEN MATCHED THEN UPDATE SET
    hit_array = CASE
        WHEN CARDINALITY(t.hit_array) = s.day_of_month - 1
            THEN ARRAY_CONCAT(t.hit_array, ARRAY[s.hit_count])
        WHEN CARDINALITY(t.hit_array) < s.day_of_month - 1
            -- Fill gaps with zeros for skipped days
            THEN ARRAY_CONCAT(
                t.hit_array,
                REPEAT(CAST(0 AS BIGINT),
                       s.day_of_month - 1 - CARDINALITY(t.hit_array)),
                ARRAY[s.hit_count])
    END
WHEN NOT MATCHED THEN INSERT ...
```

---

## 📊 Sample Results

See [sample_outputs/example_results.md](sample_outputs/example_results.md)
for full query outputs. Quick preview:

### Deduplication Impact
| Metric | Before | After |
|--------|--------|-------|
| Total rows | 12 | 7 |
| Duplicate rows removed | — | 5 |
| Data integrity | ❌ | ✅ |

### User Device Activity (Jan 5, 2023)
| user_id | Chrome activity | Safari activity | Edge activity |
|---------|----------------|-----------------|---------------|
| 501 | Jan 1,2,3,5 | — | — |
| 502 | — | Jan 1,4,6 | Jan 2 |
| 503 | — | Jan 1,3,5 | — |

### Monthly Host Metrics Array (January 2023)
| host | hit_array (Jan 1–6) | unique_visitors (Jan 1–6) |
|------|---------------------|--------------------------|
| www.techblog.com | [5, 3, 2, 2, 3, 0] | [3, 2, 1, 2, 2, 0] |
| shop.example.com | [2, 3, 2, 0, 2, 1] | [1, 2, 2, 0, 2, 1] |
| news.example.com | [0, 2, 2, 2, 2, 2] | [0, 1, 1, 1, 1, 1] |

---

## 📈 Performance at Scale

| Storage Pattern | Rows per Month | Query Speed |
|-----------------|---------------|-------------|
| Traditional daily fact | 30 rows per host | Slow (full scan) |
| Reduced monthly array | 1 row per host | Fast (single lookup) |
| Bitmap integer | 1 integer per user | Ultra-fast (bitwise AND) |

> Monthly array storage reduces row counts by **30x** compared to daily grain
> tables, enabling sub-second analytics at enterprise scale.

---

## 💼 Real-World Applications

| Industry | Use Case | Pattern Used |
|----------|----------|-------------|
| 📱 AdTech | User browser/device targeting | MAP activity datelist |
| 🛒 E-commerce | Daily active user tracking | Bitmap integers |
| 📊 SaaS Analytics | Host/tenant usage metrics | Reduced monthly arrays |
| 🏀 Sports Analytics | Clean game statistics | Deduplication |
| 🔒 Security | User session tracking | Cumulative date arrays |

---

## 🚀 How to Run

### Prerequisites
- Trino or Presto query engine
- Tables: `web_events`, `devices`, `nba_game_details`
- Apache Airflow (for `{{ ds }}` date templating) or replace manually

### Execution Order
```sql
-- Step 1: Create tables (run DDL files first)
-- ddl/query2_user_devices_cumulated_ddl.sql
-- ddl/query5_hosts_cumulated_ddl.sql
-- ddl/query7_host_activity_reduced_ddl.sql

-- Step 2: Deduplicate source data
-- queries/query1_deduplicate_game_details.sql

-- Step 3: Build cumulative tables (run daily)
-- queries/query3_generate_device_activity_datelist.sql
-- queries/query6_generate_host_activity_datelist.sql

-- Step 4: Generate derived tables
-- queries/query4_datelist_int_generation.sql
-- queries/query8_load_host_activity_reduced.sql
```

### Date Substitution
Replace `{{ ds }}` with your target date when running manually:
```sql
-- Example: replace {{ ds }} with 2023-01-15
DATE('2023-01-15')
```

---

## 🎓 About This Project

This project demonstrates production-ready fact data modeling patterns applied
to web analytics and sports data — implementing the cumulative table design,
bitmap encoding, and reduced fact table techniques used at scale in modern
data warehouses.

---

## 👩‍💻 Author

**Geeta Bhushan Ladde**
Senior Data and Quality Engineer

- 🔗 [LinkedIn](https://www.linkedin.com/in/geetasa/)
- 📧 geetas0915@gmail.com
- 📍 Folsom, CA

---

## 📚 Further Reading

- [Fact Tables — Kimball Group](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/fact-table-fundamentals/)
- [Trino Functions Reference](https://trino.io/docs/current/functions.html)
- [Bitmap Indexing Explained](https://en.wikipedia.org/wiki/Bitmap_index)

---

⭐ **If this helped you understand fact data modeling, please give it a star!**
