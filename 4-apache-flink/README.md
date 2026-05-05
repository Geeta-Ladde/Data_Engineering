# 🌊 Real-Time Web Session Analytics — Apache Flink + Kafka + PostgreSQL

> **Production-grade PyFlink streaming job that sessionizes live web traffic
> from Kafka using 5-minute session windows, grouped by IP and host,
> and writes results to PostgreSQL for downstream analytics.**

---

## 📌 Project Summary

This project implements a **real-time sessionization pipeline** that processes
a continuous stream of web events from Apache Kafka, groups them into user
sessions, and writes session-level metrics to PostgreSQL for analysis.

**The business question answered:**
> *"How many pages does a user visit in a single browsing session,
> and how does engagement differ across hosts?"*

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     STREAMING PIPELINE                          │
│                                                                 │
│  ┌──────────────┐    ┌─────────────────┐    ┌───────────────┐  │
│  │    KAFKA     │    │   APACHE FLINK  │    │  POSTGRESQL   │  │
│  │              │    │                 │    │               │  │
│  │  Web events  │───▶│  Session Window │───▶│  sessionized  │  │
│  │  (JSON)      │    │  (5-min gap)    │    │  _events      │  │
│  │              │    │                 │    │               │  │
│  │  ip          │    │  Group by:      │    │  session_start│  │
│  │  event_time  │    │  • IP address   │    │  session_end  │  │
│  │  host        │    │  • Host         │    │  ip           │  │
│  │  url         │    │                 │    │  host         │  │
│  │  referrer    │    │  Aggregate:     │    │  num_events   │  │
│  └──────────────┘    │  • COUNT events │    └───────┬───────┘  │
│                      │  • Session start│            │          │
│                      │  • Session end  │            ▼          │
│                      └─────────────────┘    ┌───────────────┐  │
│                                             │ ANALYSIS SQL  │  │
│                                             │  Queries      │  │
│                                             └───────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Session Window Logic:**
```
Same IP + Same Host + Events within 5 minutes = ONE session
Same IP + Same Host + Gap > 5 minutes         = NEW session
```

---

## 📁 Repository Structure

```
04_apache_flink/
│
├── README.md
├── requirements.txt
│
├── jobs/
│   └── sessionization_job.py       ← PyFlink streaming job
│
├── queries/
│   └── analysis_queries.sql        ← Post-processing analytics queries
│
└── sample_outputs/
    └── example_results.md          ← Sample results and insights
```

---

## 🛠️ Tech Stack

| Technology | Usage |
|------------|-------|
| **Apache Flink 1.17+** | Distributed stream processing engine |
| **PyFlink** | Python API for Flink |
| **Apache Kafka** | Real-time event streaming source |
| **SASL/SSL** | Kafka authentication and encryption |
| **Flink Session Windows** | 5-minute gap-based session detection |
| **Flink JDBC Connector** | PostgreSQL sink for session results |
| **PostgreSQL** | Analytical store for sessionized data |
| **Flink Checkpointing** | Fault tolerance and exactly-once semantics |
| **Watermarks** | Out-of-order event handling (15-second tolerance) |

---

## 💡 Key Patterns Demonstrated

### Pattern 1 — Kafka Source with SASL/SSL Authentication
Production-grade Kafka connectivity with encrypted authentication,
watermark strategy for handling late-arriving events.

```python
source_ddl = f"""
    CREATE TABLE web_events_kafka (
        ip VARCHAR,
        event_time VARCHAR,
        host VARCHAR,
        url VARCHAR,
        -- Derived timestamp column for windowing
        window_timestamp AS TO_TIMESTAMP(event_time, 'yyyy-MM-dd''T''HH:mm:ss.SSS''Z'''),
        -- Watermark: tolerate up to 15 seconds of late arrivals
        WATERMARK FOR window_timestamp AS window_timestamp - INTERVAL '15' SECOND
    ) WITH (
        'connector' = 'kafka',
        'properties.security.protocol' = 'SASL_SSL',
        'properties.sasl.mechanism' = 'PLAIN',
        ...
    );
"""
```

### Pattern 2 — Session Window Sessionization
Groups events into sessions based on inactivity gaps rather than
fixed time intervals — much more natural for user behavior modeling.

```python
# Session window: new session starts after 5 minutes of inactivity
t_env.from_path(source_table) \
    .window(
        Session.with_gap(lit(5).minutes)
               .on(col("window_timestamp"))
               .alias("w")
    ) \
    .group_by(col("w"), col("ip"), col("host")) \
    .select(
        col("w").start.alias("session_start"),
        col("w").end.alias("session_end"),
        col("ip"),
        col("host"),
        col("ip").count.alias("num_events")
    )
```

### Pattern 3 — Environment Variable Credential Management
All sensitive credentials loaded from environment variables —
never hardcoded in source code.

```python
# Credentials injected via environment variables
os.environ.get("POSTGRES_URL")
os.environ.get("KAFKA_WEB_TRAFFIC_KEY")
os.environ.get("KAFKA_WEB_TRAFFIC_SECRET")
os.environ.get("KAFKA_URL")
```

### Pattern 4 — Fault Tolerance with Checkpointing
Flink checkpointing ensures the job can recover from failures
without losing or duplicating processed events.

```python
# Checkpoint every 10 seconds for fault tolerance
env.enable_checkpointing(10000)

# Parallelism = 3 for distributed processing
env.set_parallelism(3)
```

### Pattern 5 — PostgreSQL JDBC Sink
Results written directly to PostgreSQL with a composite primary key
preventing duplicate sessions on reprocessing.

```python
sink_ddl = """
    CREATE TABLE sessionized_events (
        session_start TIMESTAMP(3),
        session_end   TIMESTAMP(3),
        ip            VARCHAR,
        host          VARCHAR,
        num_events    BIGINT,
        -- Composite PK prevents duplicate sessions
        PRIMARY KEY (session_start, ip, host) NOT ENFORCED
    ) WITH (
        'connector' = 'jdbc',
        'url' = '...',
        ...
    );
"""
```

---

## 📊 Sample Results

See [sample_outputs/example_results.md](sample_outputs/example_results.md)
for full query outputs. Quick preview:

### Average Events per Session by Host
| host | total_sessions | avg_events | unique_users |
|------|---------------|------------|--------------|
| zachwilson.techcreator.io | 28,441 | 5.1 | 12,304 |
| zachwilson.tech | 14,223 | 3.8 | 8,901 |
| lulu.techcreator.io | 5,728 | 2.9 | 3,102 |

### Session Size Distribution
| session_size | percentage | insight |
|-------------|------------|---------|
| 1 event | 31.4% | Bounce visits |
| 2-5 events | 43.7% | Normal browsing |
| 6-10 events | 17.2% | Engaged users |
| 20+ events | 1.0% | Power users |

---

## 🚀 How to Run

### Prerequisites
```bash
pip install -r requirements.txt
# Requires Java 11 for Flink
# Requires running Kafka and PostgreSQL instances
```

### Environment Variables
```bash
export POSTGRES_URL="jdbc:postgresql://localhost:5432/sessions_db"
export POSTGRES_USER="postgres"
export POSTGRES_PASSWORD="your_password"
export KAFKA_URL="your-kafka-broker:9092"
export KAFKA_TOPIC="web-events"
export KAFKA_GROUP="flink-sessionization-group"
export KAFKA_WEB_TRAFFIC_KEY="your-kafka-key"
export KAFKA_WEB_TRAFFIC_SECRET="your-kafka-secret"
```

### Run the Sessionization Job
```bash
python jobs/sessionization_job.py
```

### Run Analysis Queries
After the job has populated `sessionized_events`, run the SQL
queries against your PostgreSQL instance:
```bash
psql -d sessions_db -f queries/analysis_queries.sql
```

---

## 📈 Performance Characteristics

| Configuration | Value | Purpose |
|---------------|-------|---------|
| Checkpoint interval | 10 seconds | Fault tolerance |
| Parallelism | 3 | Distributed processing |
| Session gap | 5 minutes | Session boundary detection |
| Watermark tolerance | 15 seconds | Late event handling |

---

## 💼 Real-World Applications

| Industry | Use Case |
|----------|----------|
| 📊 Web Analytics | User session tracking and engagement metrics |
| 🛒 E-commerce | Shopping session analysis and cart abandonment |
| 🎮 Gaming | Player session duration and activity patterns |
| 📱 SaaS | Feature usage sessions and user journey analysis |
| 🔒 Security | Anomaly detection via unusual session patterns |

---

## 🎓 About This Project

This project demonstrates production-ready stream processing patterns
applied to real web traffic data — implementing the sessionization
technique used by analytics platforms to understand user engagement
across multiple hosts in real time.

---

## 👩‍💻 Author

**Geeta Bhushan Ladde**
Senior Data and Quality Engineer

- 🔗 [LinkedIn](https://www.linkedin.com/in/geetasa/)
- 📧 geetas0915@gmail.com
- 📍 Folsom, CA

---

## 📚 Further Reading

- [Apache Flink Session Windows](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/operators/windows/)
- [PyFlink Documentation](https://nightlies.apache.org/flink/flink-docs-stable/api/python/)
- [Flink Kafka Connector](https://nightlies.apache.org/flink/flink-docs-stable/docs/connectors/datastream/kafka/)

---

⭐ **If this helped you understand real-time stream processing, please give it a star!**
