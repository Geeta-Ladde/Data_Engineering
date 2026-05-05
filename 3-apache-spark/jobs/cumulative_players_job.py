# cumulative_players_job.py
# PySpark job that executes the cumulative players SparkSQL query

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType, FloatType, BooleanType


def run_cumulative_players_job(last_season_path, current_season_path, output_path, target_season):
    """
    PySpark job to run cumulative player statistics building

    Args:
        last_season_path: Path to existing cumulative player data
        current_season_path: Path to current season individual statistics
        output_path: Path to write results
        target_season: Target season year (e.g., 1998)
    """

    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("CumulativePlayersJob") \
        .getOrCreate()

    try:
        # Define season stats struct schema
        season_stats_schema = StructType([
            StructField("season", IntegerType(), True),
            StructField("pts", FloatType(), True),
            StructField("ast", FloatType(), True),
            StructField("reb", FloatType(), True),
            StructField("weight", FloatType(), True)
        ])

        # Define schemas
        players_schema = StructType([
            StructField("player_name", StringType(), True),
            StructField("height", StringType(), True),
            StructField("college", StringType(), True),
            StructField("country", StringType(), True),
            StructField("draft_year", IntegerType(), True),
            StructField("draft_round", IntegerType(), True),
            StructField("draft_number", IntegerType(), True),
            StructField("seasons", ArrayType(season_stats_schema), True),
            StructField("scoring_class", StringType(), True),
            StructField("is_active", BooleanType(), True),
            StructField("current_season", IntegerType(), True)
        ])

        player_seasons_schema = StructType([
            StructField("player_name", StringType(), True),
            StructField("season", IntegerType(), True),
            StructField("pts", FloatType(), True),
            StructField("ast", FloatType(), True),
            StructField("reb", FloatType(), True),
            StructField("weight", FloatType(), True),
            StructField("height", StringType(), True),
            StructField("college", StringType(), True),
            StructField("country", StringType(), True),
            StructField("draft_year", IntegerType(), True),
            StructField("draft_round", IntegerType(), True),
            StructField("draft_number", IntegerType(), True)
        ])

        # Load data
        players_df = spark.read.schema(players_schema).parquet(last_season_path)
        player_seasons_df = spark.read.schema(player_seasons_schema).parquet(current_season_path)

        # Register as temporary views for SparkSQL
        players_df.createOrReplaceTempView("players")
        player_seasons_df.createOrReplaceTempView("player_seasons")

        # Calculate previous season (target_season - 1)
        previous_season = target_season - 1

        # Execute the SparkSQL query with parameterized seasons
        result = spark.sql(f"""
            WITH last_season AS (
                SELECT * FROM players
                WHERE current_season = {previous_season}
            ), 
            this_season AS (
                SELECT * FROM player_seasons
                WHERE season = {target_season}
            )
            SELECT
                COALESCE(ls.player_name, ts.player_name) as player_name,
                COALESCE(ls.height, ts.height) as height,
                COALESCE(ls.college, ts.college) as college,
                COALESCE(ls.country, ts.country) as country,
                COALESCE(ls.draft_year, ts.draft_year) as draft_year,
                COALESCE(ls.draft_round, ts.draft_round) as draft_round,
                COALESCE(ls.draft_number, ts.draft_number) as draft_number,

                -- Handle seasons array: combine existing seasons with new season
                CASE 
                    WHEN ts.season IS NOT NULL THEN
                        CASE 
                            WHEN ls.seasons IS NOT NULL THEN
                                array_union(
                                    ls.seasons,
                                    array(struct(
                                        ts.season as season,
                                        ts.pts as pts,
                                        ts.ast as ast,
                                        ts.reb as reb,
                                        ts.weight as weight
                                    ))
                                )
                            ELSE
                                array(struct(
                                    ts.season as season,
                                    ts.pts as pts,
                                    ts.ast as ast,
                                    ts.reb as reb,
                                    ts.weight as weight
                                ))
                        END
                    ELSE 
                        COALESCE(ls.seasons, array())
                END as seasons,

                -- Scoring class calculation based on points
                CASE
                    WHEN ts.season IS NOT NULL THEN
                        CASE 
                            WHEN ts.pts > 20 THEN 'star'
                            WHEN ts.pts > 15 THEN 'good'
                            WHEN ts.pts > 10 THEN 'average'
                            ELSE 'bad' 
                        END
                    ELSE ls.scoring_class
                END as scoring_class,

                -- Is active flag
                CASE WHEN ts.season IS NOT NULL THEN true ELSE false END as is_active,

                -- Current season (parameterized)
                {target_season} AS current_season

            FROM last_season ls
            FULL OUTER JOIN this_season ts
            ON ls.player_name = ts.player_name
        """)

        # Write results
        result.write.mode("overwrite").parquet(output_path)
        print(f"Cumulative players job completed successfully. Results written to {output_path}")

    finally:
        # Only stop spark when running as main script, not when called from tests
        import __main__
        if hasattr(__main__, '__file__') and __main__.__file__ == __file__:
            spark.stop()


if __name__ == "__main__":
    # Example usage
    run_cumulative_players_job(
        last_season_path="data/players.parquet",
        current_season_path="data/player_seasons.parquet",
        output_path="output/players_cumulative.parquet",
        target_season=1998
    )