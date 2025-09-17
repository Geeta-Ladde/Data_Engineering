PostgreSQL to SparkSQL Conversions
This project converts two PostgreSQL queries from Week 1-2 dimensional modeling to SparkSQL jobs.
Query 1: Incremental SCD Type 2 (Players)
Original PostgreSQL Query:
sqlCREATE TYPE scd_type AS (
    scoring_class scoring_class,
    is_active boolean,
    start_season integer,
    end_season integer
);

WITH last_season_scd AS (
    SELECT * FROM players_scd 
    WHERE current_season = 2021
        AND end_season = 2021
),

historical_scd AS (
    SELECT 
        player_name,
        scoring_class,
        is_active,
        start_season,
        end_season
    FROM players_scd 
    WHERE current_season = 2021 
        AND end_season < 2021
),

this_season_data AS (
    SELECT * FROM player_seasons 
    WHERE season = 2022
),

unchanged_records AS (
    SELECT 
        ts.player_name,
        ts.scoring_class,
        ts.is_active,
        ls.start_season,
        2022 as end_season
    FROM this_season_data ts
    JOIN last_season_scd ls 
        ON ts.player_name = ls.player_name
    WHERE ts.scoring_class = ls.scoring_class 
        AND ts.is_active = ls.is_active
),

changed_records AS (
    SELECT 
        ts.player_name,
        unnest(ARRAY[
            ROW(
                ls.scoring_class,
                ls.is_active,
                ls.start_season,
                ls.end_season
            )::scd_type,
            ROW(
                ts.scoring_class,
                ts.is_active,
                2022,
                2022
            )::scd_type
        ]) as records
    FROM this_season_data ts
    JOIN last_season_scd ls 
        ON ts.player_name = ls.player_name
    WHERE (ts.scoring_class <> ls.scoring_class 
           OR ts.is_active <> ls.is_active)
),

unnested_changed_records AS (
    SELECT 
        player_name,
        (records).scoring_class,
        (records).is_active,
        (records).start_season,
        (records).end_season
    FROM changed_records
),

new_records AS (
    SELECT 
        ts.player_name,
        ts.scoring_class,
        ts.is_active,
        2022 as start_season,
        2022 as end_season
    FROM this_season_data ts
    LEFT JOIN last_season_scd ls 
        ON ts.player_name = ls.player_name
    WHERE ls.player_name IS NULL
),

dropped_records AS (
    SELECT 
        ls.player_name,
        ls.scoring_class,
        ls.is_active,
        ls.start_season,
        ls.end_season
    FROM last_season_scd ls
    LEFT JOIN this_season_data ts 
        ON ls.player_name = ts.player_name
    WHERE ts.player_name IS NULL
)

SELECT *, 2022 as current_season FROM (
    SELECT * FROM unchanged_records
    UNION ALL
    SELECT * FROM unnested_changed_records
    UNION ALL
    SELECT * FROM new_records
    UNION ALL
    SELECT * FROM dropped_records
    UNION ALL
    SELECT * FROM historical_scd
);
SparkSQL Conversion:
Converted to src/jobs/incremental_scd_job.py using:

Replaced PostgreSQL ARRAY/ROW/unnest with SparkSQL array and struct functions
Used null-safe equality operator <=> instead of = and IS NULL patterns
Structured as reusable PySpark job with parameterized seasons


Query 2: Cumulative Table (Players)
Original PostgreSQL Query:
sqlSELECT 
    COALESCE(ls.player_name, ts.player_name) as player_name,
    CASE 
        WHEN ts.season IS NOT NULL THEN 
            CASE 
                WHEN ts.pts > 20 THEN 'star'
                WHEN ts.pts > 15 THEN 'good'
                WHEN ts.pts > 10 THEN 'average'
                ELSE 'bad'
            END::scoring_class
        ELSE ls.scoring_class
    END as scoring_class,
    CASE 
        WHEN ts.season IS NOT NULL THEN true
        ELSE false
    END as is_active,
    COALESCE(
        ls.seasons || ARRAY[ROW(
            ts.season,
            ts.gp,
            ts.pts,
            ts.reb,
            ts.ast
        )::season_stats],
        ARRAY[ROW(
            ts.season,
            ts.gp,
            ts.pts,
            ts.reb,
            ts.ast
        )::season_stats]
    ) as seasons,
    1998 as current_season
FROM (
    SELECT * FROM players 
    WHERE current_season = 1997
) ls
FULL OUTER JOIN (
    SELECT * FROM player_seasons 
    WHERE season = 1998
) ts ON ls.player_name = ts.player_name;
SparkSQL Conversion:
Converted to src/jobs/cumulative_players_job.py using:

Replaced PostgreSQL ARRAY[ROW(...)] with SparkSQL array(struct(...))
Used array_union instead of || for array concatenation
Maintained FULL OUTER JOIN logic with proper null handling


How to Run
Jobs:
bash# Incremental SCD Job
spark-submit src/jobs/incremental_scd_job.py \
  --last_scd_path data/players_scd/ \
  --current_season_path data/player_seasons_2022/ \
  --output_path data/players_scd_updated/

# Cumulative Players Job  
spark-submit src/jobs/cumulative_players_job.py \
  --last_season_path data/players_1997/ \
  --current_season_path data/player_seasons_1998/ \
  --output_path data/players_1998/
Tests:
bashpython -m pytest src/tests/ -v
Key Differences: PostgreSQL vs SparkSQL

Type Definitions: PostgreSQL custom types replaced with SparkSQL StructType schemas
Array Operations: || becomes array_union, ARRAY[ROW(...)] becomes array(struct(...))
Null Safety: PostgreSQL IS NULL/IS NOT NULL becomes SparkSQL <=> operator
UNNEST: PostgreSQL unnest() replaced with SparkSQL explode() where needed
Job Structure: Added proper SparkSession management and file I/O operations
