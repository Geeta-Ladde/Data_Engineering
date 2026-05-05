# incremental_scd_job.py
# PySpark job that executes the SCD SparkSQL query

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, BooleanType, IntegerType


def run_incremental_scd_job(last_scd_path, current_season_path, output_path, previous_season, current_season):
    """
    PySpark job to run incremental SCD Type 2 processing

    Args:
        last_scd_path: Path to existing SCD table data
        current_season_path: Path to current season player data
        output_path: Path to write results
        previous_season: Previous season year (e.g., 2021)
        current_season: Current season year (e.g., 2022)
    """

    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("IncrementalSCDJob") \
        .getOrCreate()

    try:
        # Define schemas
        players_scd_schema = StructType([
            StructField("player_name", StringType(), True),
            StructField("scoring_class", StringType(), True),
            StructField("is_active", BooleanType(), True),
            StructField("start_season", IntegerType(), True),
            StructField("end_season", IntegerType(), True),
            StructField("current_season", IntegerType(), True)
        ])

        players_schema = StructType([
            StructField("player_name", StringType(), True),
            StructField("scoring_class", StringType(), True),
            StructField("is_active", BooleanType(), True),
            StructField("current_season", IntegerType(), True)
        ])

        # Load data
        players_scd_df = spark.read.schema(players_scd_schema).parquet(last_scd_path)
        players_df = spark.read.schema(players_schema).parquet(current_season_path)

        # Register as temporary views for SparkSQL
        players_scd_df.createOrReplaceTempView("players_scd")
        players_df.createOrReplaceTempView("players")

        # Execute the SparkSQL query with parameterized seasons
        result = spark.sql(f"""
           -- Fixed SCD query that handles dropped players and null-safe comparisons
WITH last_season_scd AS (
    SELECT * FROM players_scd
    WHERE current_season = {previous_season}
    AND end_season = {previous_season}
),
historical_scd AS (
    SELECT
        player_name,
        scoring_class,
        is_active,
        start_season,
        end_season
    FROM players_scd
    WHERE current_season = {previous_season}
    AND end_season < {previous_season}
),
this_season_data AS (
    SELECT * FROM players
    WHERE current_season = {current_season}
),
unchanged_records AS (
    SELECT
        ts.player_name,
        ts.scoring_class,
        ts.is_active,
        ls.start_season,
        {current_season} as end_season
    FROM this_season_data ts
    JOIN last_season_scd ls
    ON ls.player_name = ts.player_name
    -- Use null-safe equality for comparisons
    WHERE (ts.scoring_class <=> ls.scoring_class) 
    AND (ts.is_active <=> ls.is_active)
),
changed_records_old AS (
    SELECT
        ls.player_name,
        ls.scoring_class,
        ls.is_active,
        ls.start_season,
        ls.end_season
    FROM this_season_data ts
    LEFT JOIN last_season_scd ls
    ON ls.player_name = ts.player_name
    -- Use null-safe inequality for change detection
    WHERE NOT ((ts.scoring_class <=> ls.scoring_class) AND (ts.is_active <=> ls.is_active))
    AND ls.player_name IS NOT NULL
),
changed_records_new AS (
    SELECT
        ts.player_name,
        ts.scoring_class,
        ts.is_active,
        {current_season} AS start_season,
        {current_season} AS end_season
    FROM this_season_data ts
    LEFT JOIN last_season_scd ls
    ON ls.player_name = ts.player_name
    WHERE NOT ((ts.scoring_class <=> ls.scoring_class) AND (ts.is_active <=> ls.is_active))
    AND ls.player_name IS NOT NULL
),
changed_records AS (
    SELECT * FROM changed_records_old
    UNION ALL
    SELECT * FROM changed_records_new
),
new_records AS (
    SELECT
        ts.player_name,
        ts.scoring_class,
        ts.is_active,
        {current_season} AS start_season,
        {current_season} AS end_season
    FROM this_season_data ts
    LEFT JOIN last_season_scd ls
    ON ts.player_name = ts.player_name
    WHERE ls.player_name IS NULL
),
-- NEW: Handle dropped players (existed in previous season, missing in current season)
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
SELECT *, {current_season} AS current_season FROM (
    SELECT * FROM historical_scd
    UNION ALL
    SELECT * FROM unchanged_records
    UNION ALL
    SELECT * FROM changed_records
    UNION ALL
    SELECT * FROM new_records
    UNION ALL
    SELECT * FROM dropped_records  -- Include dropped players
) final_result
        """)

        # Write results
        result.write.mode("overwrite").parquet(output_path)
        print(f"SCD job completed successfully. Results written to {output_path}")

    finally:
        # Only stop spark when running as main script, not when called from tests
        import __main__
        if hasattr(__main__, '__file__') and __main__.__file__ == __file__:
            spark.stop()


if __name__ == "__main__":
    # Example usage
    run_incremental_scd_job(
        last_scd_path="data/players_scd.parquet",
        current_season_path="data/players.parquet",
        output_path="output/players_scd_updated.parquet",
        previous_season=2021,
        current_season=2022
    )