# 👩‍💻 Geeta Bhushan Ladde — Data Engineering Portfolio

> **11+ years of IT experience specializing in Data Engineering, Data Quality,
> ETL/ELT pipeline development, and cloud-native data platforms across
> AWS, Azure, Databricks, and Snowflake.**

---

## 👋 About Me

I am a Senior Data and Quality Engineer with over 11 years of experience
building and validating large-scale data pipelines across the full modern
data stack. My expertise spans data quality engineering, ETL/ELT development,
distributed processing with Apache Spark and Flink, cloud data warehousing,
and SQL analytics.

**Core Technical Skills:**

| Area | Technologies |
|------|-------------|
| **Languages** | Python, PySpark, SQL, Scala |
| **Big Data** | Apache Spark, Apache Flink, Kafka |
| **Cloud — AWS** | S3, Glue, Lambda, Redshift, Athena, EMR, Step Functions, SNS, SQS |
| **Cloud — Azure** | Databricks, Azure Data Factory, Delta Lake |
| **Data Warehouses** | Snowflake, AWS Redshift, Google BigQuery |
| **Databases** | PostgreSQL, DynamoDB, Trino/Presto |
| **Orchestration** | Apache Airflow (MWAA), AWS Step Functions |
| **Testing** | pytest, Data Quality Validation, Schema Testing |
| **Visualization** | Tableau |

**Certifications:**
- 🏆 AWS Certified Data Engineer — Associate (2024)
- 🏆 Certified Data Engineer — DataExpert.io (2024)
- 🏆 Databricks Fundamentals Accreditation (2024)
- 🏆 Databricks Generative AI Fundamentals (2024)
- 🏆 Microsoft Azure Fundamentals AZ-900 (2022)
- 🏆 Tricentis TOSCA Certified Automation Specialist (2020)

---

## 📁 Portfolio Projects

This repository showcases 8 end-to-end data engineering projects covering
dimensional modeling, fact data modeling, distributed processing, real-time
streaming, advanced analytics, and product experimentation — built using
production-grade patterns and best practices.

---

### 1️⃣ [Dimensional Data Modeling](./1-dimension-data-modeling)
**Tech:** PostgreSQL · SCD Type 2 · Window Functions · CTEs · PL/pgSQL

Implements a complete data warehouse dimensional model tracking actor
performance quality over time using Slowly Changing Dimensions Type 2,
cumulative table generation, and incremental data processing patterns.

**Key patterns:** Array of composite types · Incremental FULL JOIN loads ·
SCD Type 2 change detection with LAG() · Idempotent upserts with ON CONFLICT

---

### 2️⃣ [Fact Data Modeling](./2-fact-data-modeling)
**Tech:** Trino/Presto · MAP Aggregation · Bitmap Encoding · MERGE · ARRAY

Builds a complete fact data modeling pipeline tracking user web activity
across devices and hosts over time, with bitmap integer encoding for
ultra-fast activity queries and monthly reduced fact tables.

**Key patterns:** MAP<VARCHAR, ARRAY<DATE>> activity tracking ·
Bitmap integer encoding · MERGE for idempotent incremental loads ·
Gap-filling with REPEAT() · Deduplication with ROW_NUMBER()

---

### 3️⃣ [Apache Spark — PySpark ETL Jobs](./3-apache-spark)
**Tech:** PySpark · SparkSQL · pytest · Parquet · Broadcast Join · Bucket Join

Three production-grade PySpark jobs with full pytest unit test coverage —
implementing SCD Type 2 migration from PostgreSQL to Spark, cumulative
season array accumulation, and Halo 5 gaming analytics with join strategy
comparisons.

**Key patterns:** Explicit StructType schemas · Parameterized Spark jobs ·
12 pytest unit tests covering edge cases · Broadcast vs bucket join comparison ·
Null-safe equality with <=> · sortWithinPartitions optimization

---

### 4️⃣ [Apache Flink — Real-Time Sessionization](./4-apache-flink)
**Tech:** PyFlink · Apache Kafka · PostgreSQL · SASL/SSL · Session Windows

Production-grade real-time streaming job that sessionizes live web traffic
from Kafka using 5-minute session windows grouped by IP and host, writing
results to PostgreSQL for downstream analytics.

**Key patterns:** Kafka source with SASL/SSL authentication ·
Session window sessionization · Watermark strategy for late events ·
Checkpointing for fault tolerance · Environment variable credential management ·
PostgreSQL JDBC sink with composite primary key

---

### 5️⃣ [Advanced SQL Analytical Patterns](./5-applying-analytical-patterns)
**Tech:** PostgreSQL · GROUPING SETS · Rolling Windows · Gap-and-Island · GENERATE_SERIES

Seven advanced SQL queries on NBA game data demonstrating the analytical
patterns used in production business intelligence pipelines — from
multi-dimensional aggregations to streak detection.

**Key patterns:** GROUPING SETS across 3 dimensions ·
Rolling 90-game window with ROWS BETWEEN 89 PRECEDING ·
Gap-and-island streak detection · Season-over-season state change tracking ·
RANK() for tie-safe results · CROSS JOIN with GENERATE_SERIES

---

### 6️⃣ [Data Pipeline Maintenance & Operations](./6-data-pipeline-maintenance)
**Tech:** Runbook Design · On-Call Planning · Incident Response · SLA Management

Complete operational framework for a 4-person data engineering team
managing 5 production pipelines — covering ownership matrix, fair on-call
rotation with holiday coverage, detailed runbooks for investor-facing
pipelines, and incident response protocols.

**Key patterns:** Pipeline ownership matrix · P0/P1/P2 severity framework ·
Quarterly on-call rotation with holiday policy ·
Investor reporting runbooks with failure scenario analysis ·
Escalation path definition

---

### 7️⃣ [Data Visualization — Halo 5 Gaming Dashboards](./7-data-visualization)
**Tech:** Tableau Public · PySpark · CSV · Halo 5 Dataset

Two interactive Tableau Public dashboards analyzing 50,000+ Halo 5
match records — an executive KPI summary and an exploratory drill-down
dashboard with dynamic filters. Data was pre-processed using PySpark
before visualization.

**Live Dashboards:**
- 🎯 [Executive Dashboard](https://public.tableau.com/app/profile/geeta.ladde/viz/Halo_Executive_Dashboard/Dashboard1?publish=yes)
- 🔍 [Exploratory Dashboard](https://public.tableau.com/app/profile/geeta.ladde/viz/Book1_17637733241420/ExploratoryDashboard?publish=yes)

---

### 8️⃣ [KPIs & Experimentation — Spotify Analysis](./8-kpis-and-experimentation)
**Tech:** A/B Testing · Metric Framework Design · Product Analytics

Three detailed A/B experiment designs for Spotify covering hypothesis
formation, test cell allocation with 400K–600K users per experiment,
leading and lagging metric predictions, counter metrics, and strategic
prioritization recommendations.

**Key patterns:** Hypothesis-driven experiment design ·
Control and treatment group allocation ·
Leading vs lagging metric separation ·
Counter metric monitoring ·
Privacy-first experimentation design

---

## 🔗 Connect

**Geeta Bhushan Ladde**
Senior Data and Quality Engineer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/geetasa/)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black)](https://github.com/Geeta-Ladde)

- 📧 geetas0915@gmail.com
- 📍 California

---

⭐ **If you find this portfolio helpful, please give it a star!**
