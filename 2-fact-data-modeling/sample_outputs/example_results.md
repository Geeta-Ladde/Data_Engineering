# 📊 Sample Query Results

---

## Query 1 — Deduplication Results

**Before deduplication:** 12 rows (duplicates present)
**After deduplication:** 7 unique rows

| game_id | team_id | player_name | pts | reb | ast | plus_minus |
|---------|---------|-------------|-----|-----|-----|------------|
| 22300001 | LAL | LeBron James | 21 | 7 | 8 | +12 |
| 22300001 | LAL | Anthony Davis | 26 | 12 | 2 | +12 |
| 22300001 | GSW | Stephen Curry | 31 | 4 | 6 | -12 |
| 22300001 | GSW | Klay Thompson | 18 | 3 | 2 | -12 |
| 22300002 | BOS | Jayson Tatum | 28 | 8 | 4 | +8 |
| 22300002 | BOS | Jaylen Brown | 23 | 5 | 3 | +8 |
| 22300002 | CHI | Zach LaVine | 29 | 4 | 5 | -8 |

> **5 duplicate rows removed** using ROW_NUMBER() OVER (PARTITION BY game_id, team_id, player_id)

---

## Query 2 — user_devices_cumulated Table Structure

After running cumulative load for January 2023:

| user_id | device_activity_datelist | date |
|---------|--------------------------|------|
| 501 | {Chrome: [2023-01-01, 2023-01-02, 2023-01-03, 2023-01-05]} | 2023-01-05 |
| 502 | {Firefox: [2023-01-01], Edge: [2023-01-02], Firefox: [2023-01-04, 2023-01-06]} | 2023-01-06 |
| 503 | {Safari: [2023-01-01, 2023-01-03, 2023-01-05]} | 2023-01-05 |
| 504 | {Chrome: [2023-01-02, 2023-01-03]} | 2023-01-03 |
| 505 | {Safari: [2023-01-02, 2023-01-04]} | 2023-01-04 |

> One row per user per date — full browser activity history accumulated over time

---

## Query 4 — Bitmap Integer Representation

Converting date arrays to integer bitmaps (anchor = 2023-01-01):

| user_id | browser_type | activity_dates | datelist_int | binary_repr |
|---------|-------------|----------------|--------------|-------------|
| 501 | Chrome | Jan 1,2,3,5 | 23 | ...010111 |
| 503 | Safari | Jan 1,3,5 | 21 | ...010101 |
| 504 | Chrome | Jan 2,3 | 6 | ...000110 |

**How bitmap works:**
```
Day:    Jan 7  Jan 6  Jan 5  Jan 4  Jan 3  Jan 2  Jan 1
Bit:      64     32     16      8      4      2      1

User 501 active on Jan 1,2,3,5:
  Jan 1 → bit 0 = 1
  Jan 2 → bit 1 = 2
  Jan 3 → bit 2 = 4
  Jan 5 → bit 4 = 16
  Total = 1 + 2 + 4 + 16 = 23
```

> Bitmaps enable lightning-fast activity checks using bitwise AND operations

---

## Query 6 — hosts_cumulated Results

| host | host_activity_datelist | date |
|------|----------------------|------|
| www.techblog.com | [2023-01-01, 2023-01-02, 2023-01-03, 2023-01-04, 2023-01-05] | 2023-01-05 |
| shop.example.com | [2023-01-01, 2023-01-02, 2023-01-03, 2023-01-05, 2023-01-06] | 2023-01-06 |
| news.example.com | [2023-01-02, 2023-01-03, 2023-01-04, 2023-01-05, 2023-01-06] | 2023-01-06 |

---

## Query 8 — host_activity_reduced Monthly Results

After loading January 2023 day by day:

| host | month | hit_array | unique_visitors_array |
|------|-------|-----------|-----------------------|
| www.techblog.com | 2023-01-01 | [5, 3, 2, 2, 3, 0, ...] | [3, 2, 1, 2, 2, 0, ...] |
| shop.example.com | 2023-01-01 | [2, 3, 2, 0, 2, 1, ...] | [1, 2, 2, 0, 2, 1, ...] |
| news.example.com | 2023-01-01 | [0, 2, 2, 2, 2, 2, ...] | [0, 1, 1, 1, 1, 1, ...] |

**Array index = day of month - 1:**
- `hit_array[0]` = hits on Jan 1
- `hit_array[1]` = hits on Jan 2
- `0` = no activity that day (gap filled automatically)

**Gap filling example:**
```
Day 1 loaded:  hit_array = [5]
Day 2 loaded:  hit_array = [5, 3]
Day 4 loaded:  hit_array = [5, 3, 0, 2]  ← Day 3 auto-filled with 0
Day 5 loaded:  hit_array = [5, 3, 0, 2, 3]
```

---

## Performance Insight

| Pattern | Rows Stored | Query Speed |
|---------|-------------|-------------|
| Traditional daily fact table | 1 row per host per day | Slow (many rows to scan) |
| Reduced monthly array fact | 1 row per host per month | Fast (single row lookup) |
| Bitmap integer | 1 integer per user per browser | Ultra-fast (bitwise AND) |

> Reduced fact tables with array storage cut row counts by **30x** compared to
> traditional daily grain tables, enabling sub-second analytics at scale.
