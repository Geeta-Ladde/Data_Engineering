PostgreSQL to SparkSQL Conversions

This project demonstrates how to convert PostgreSQL queries into PySpark jobs.
It focuses on Incremental SCD Type 2 and Cumulative Player Tables, showing how SQL constructs map into SparkSQL functions.

📌 Query 1: Incremental SCD Type 2 (Players)
🐘 Original PostgreSQL Query
CREATE TYPE scd_type AS (
    scoring_class scoring_class,
    is_active boolean,
    start_season integer,
    end_season integer
);

WITH last_season_scd AS (
    SELECT * FROM players_scd
    WHERE current_season = 2021 AND end_season = 2021
),
...

⚡ SparkSQL Conversion

Implemented in src/jobs/incremental_scd_job.py

PostgreSQL ARRAY / ROW / unnest → SparkSQL array, struct, explode

Null-safe equality (=, IS NULL) → SparkSQL <=>

Structured as a reusable PySpark job with parameterized seasons

📌 Query 2: Cumulative Table (Players)
🐘 Original PostgreSQL Query
SELECT COALESCE(ls.player_name, ts.player_name) as player_name,
       CASE WHEN ts.season IS NOT NULL
            THEN CASE
                     WHEN ts.pts > 20 THEN 'star'
                     WHEN ts.pts > 15 THEN 'good'
                     WHEN ts.pts > 10 THEN 'average'
                     ELSE 'bad'
                 END::scoring_class
            ELSE ls.scoring_class
       END as scoring_class,
       ...

⚡ SparkSQL Conversion

Implemented in src/jobs/cumulative_players_job.py

PostgreSQL ARRAY[ROW(...)] → SparkSQL array(struct(...))

Array concatenation || → SparkSQL array_union

Preserved FULL OUTER JOIN with proper null handling

▶️ How to Run Jobs

Incremental SCD Job

spark-submit src/jobs/incremental_scd_job.py \
  --last_scd_path data/players_scd/ \
  --current_season_path data/player_seasons_2022/ \
  --output_path data/players_scd_updated/


Cumulative Players Job

spark-submit src/jobs/cumulative_players_job.py \
  --last_season_path data/players_1997/ \
  --current_season_path data/player_seasons_1998/ \
  --output_path data/players_1998/

🧪 Running Tests
python -m pytest src/tests/ -v

🔑 Key Differences: PostgreSQL vs SparkSQL
Feature	PostgreSQL Example	SparkSQL Equivalent
Custom Types	CREATE TYPE scd_type ...	StructType schemas
Array Ops	`	
Null Handling	IS NULL / IS NOT NULL	<=> (null-safe equality)
Unnesting	unnest()	explode()
Job Structure	SQL script execution	PySpark job with I/O + session

✨ This project demonstrates how SQL-based ETL logic can be migrated into Spark for scalable, production-ready pipelines.