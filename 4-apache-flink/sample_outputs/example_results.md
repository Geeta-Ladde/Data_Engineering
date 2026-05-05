# 📊 Sample Query Results — Sessionized Web Events

---

## Sessionized Events Table — Sample Output

After running the Flink sessionization job, the `sessionized_events`
table in PostgreSQL looks like this:

| session_start | session_end | ip | host | num_events |
|---------------|-------------|-----|------|------------|
| 2023-01-15 08:01:12 | 2023-01-15 08:04:45 | 192.168.1.10 | zachwilson.techcreator.io | 5 |
| 2023-01-15 08:02:33 | 2023-01-15 08:06:10 | 10.0.0.25 | zachwilson.techcreator.io | 3 |
| 2023-01-15 09:15:00 | 2023-01-15 09:22:18 | 192.168.1.10 | zachwilson.tech | 8 |
| 2023-01-15 10:30:45 | 2023-01-15 10:31:02 | 172.16.0.5 | lulu.techcreator.io | 1 |
| 2023-01-15 11:00:00 | 2023-01-15 11:08:33 | 10.0.0.50 | zachwilson.techcreator.io | 12 |

> A new session starts when the same IP has no activity on the same host
> for more than 5 minutes. The same user visiting at 8:01 AM and again
> at 9:15 AM produces TWO separate sessions.

---

## Query 1 — Average Events per Session (Tech Creator hosts)

```sql
SELECT
    'All Tech Creator Hosts' as category,
    COUNT(*) as total_sessions,
    AVG(num_events) as avg_events_per_session,
    ...
FROM sessionized_events
WHERE host LIKE '%.techcreator.io';
```

| category | total_sessions | avg_events | min_events | max_events | median |
|----------|---------------|------------|------------|------------|--------|
| All Tech Creator Hosts | 48,392 | 4.2 | 1 | 187 | 3 |

---

## Query 2 — Host Comparison

| host | total_sessions | unique_users | avg_events | total_events |
|------|---------------|--------------|------------|--------------|
| zachwilson.techcreator.io | 28,441 | 12,304 | 5.1 | 145,049 |
| zachwilson.tech | 14,223 | 8,901 | 3.8 | 54,047 |
| lulu.techcreator.io | 5,728 | 3,102 | 2.9 | 16,611 |

> **Key Insight:** zachwilson.techcreator.io has the highest engagement
> with 5.1 events per session on average — users explore more pages per visit.

---

## Session Duration Analysis

| host | avg_duration_mins | min_duration_mins | max_duration_mins |
|------|------------------|------------------|------------------|
| zachwilson.techcreator.io | 3.2 | 0.0 | 4.9 |
| zachwilson.tech | 2.8 | 0.0 | 4.9 |
| lulu.techcreator.io | 1.9 | 0.0 | 4.8 |

> Sessions are capped at just under 5 minutes because the session gap
> closes the window after 5 minutes of inactivity.

---

## Session Size Distribution

| host | session_size | count | percentage |
|------|-------------|-------|------------|
| zachwilson.techcreator.io | 1 event | 8,923 | 31.4% |
| zachwilson.techcreator.io | 2-5 events | 12,441 | 43.7% |
| zachwilson.techcreator.io | 6-10 events | 4,892 | 17.2% |
| zachwilson.techcreator.io | 11-20 events | 1,892 | 6.7% |
| zachwilson.techcreator.io | 20+ events | 293 | 1.0% |

> **Key Insight:** 75% of sessions have 5 or fewer events — most users
> visit briefly. Power users (20+ events) represent only 1% but are
> valuable engagement targets.

---

## Peak Hours Analysis

| host | hour_of_day | session_count | avg_events |
|------|-------------|---------------|------------|
| zachwilson.techcreator.io | 9 | 3,241 | 5.8 |
| zachwilson.techcreator.io | 10 | 3,892 | 5.4 |
| zachwilson.techcreator.io | 14 | 3,104 | 5.1 |
| zachwilson.techcreator.io | 20 | 2,891 | 4.9 |
| zachwilson.techcreator.io | 3 | 412 | 2.1 |

> **Key Insight:** Peak engagement is 9-10 AM — morning hours have both
> highest volume and highest events per session. Late night (3 AM) has
> low volume and shallow sessions.

---

## How Session Windows Work

```
IP: 192.168.1.10  Host: zachwilson.techcreator.io

Timeline:
  08:01 ── event ──────────────────────────────────────────
  08:02 ── event ──┐
  08:04 ── event ──┤ SESSION 1 (5 events, 3.5 min)
  08:05 ── event ──┤
  08:04:30 event ──┘
  
  [--- 5 minute gap = session boundary ---]
  
  09:15 ── event ──┐
  09:18 ── event ──┤ SESSION 2 (8 events, 7.3 min)
  09:19 ── event ──┘
  ...
```

> The 5-minute gap window means: if the same IP visits the same host
> within 5 minutes, it's the SAME session. After 5 minutes of silence,
> the next visit starts a NEW session.
