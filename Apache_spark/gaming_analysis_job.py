from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pyspark.sql.functions as F
from pyspark.sql.functions import countDistinct, broadcast, avg, sum, count, desc, col


def create_spark_session():
    """Create and configure Spark session"""
    spark = SparkSession.builder \
        .appName("Gaming Data Analysis - Spark Fundamentals Homework") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()

    # Disable automatic broadcast join as required
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")

    return spark


def load_and_bucket_tables(spark):
    """Load tables and apply bucketing strategy"""

    # Load the main tables from CSV files in the data folder
    # From src/jobs/ we need to go up two levels to reach the data folder
    match_details = spark.read.csv("../../data/match_details.csv", header=True, inferSchema=True)
    matches = spark.read.csv("../../data/matches.csv", header=True, inferSchema=True)
    medals_matches_players = spark.read.csv("../../data/medals_matches_players.csv", header=True, inferSchema=True)
    medals = spark.read.csv("../../data/medals.csv", header=True, inferSchema=True)
    maps = spark.read.csv("../../data/maps.csv", header=True, inferSchema=True)

    # Bucket the large tables on match_id with 16 buckets
    # This optimizes joins by co-locating data with the same match_id
    match_details_bucketed = match_details.repartition(16, "match_id")
    matches_bucketed = matches.repartition(16, "match_id")
    medals_matches_players_bucketed = medals_matches_players.repartition(16, "match_id")

    # Explicitly broadcast the small dimension tables
    medals_broadcast = F.broadcast(medals)
    maps_broadcast = F.broadcast(maps)

    return {
        "match_details": match_details_bucketed,
        "matches": matches_bucketed,
        "medals_matches_players": medals_matches_players_bucketed,
        "medals": medals_broadcast,
        "maps": maps_broadcast
    }


def perform_analysis(tables):
    """Perform the required analysis questions"""

    # Join all tables together with aliases to avoid column conflicts
    match_details = tables["match_details"].alias("md")
    matches = tables["matches"].alias("m")
    medals_matches_players = tables["medals_matches_players"].alias("mmp")
    medals = tables["medals"].alias("medals")
    maps = tables["maps"].alias("maps")

    # Start with match_details and join with matches (bucket join)
    main_df = match_details.join(matches, "match_id", "inner")

    # Join with medals_matches_players (bucket join)
    main_df = main_df.join(medals_matches_players, ["match_id", "player_gamertag"], "left")

    # Join with broadcasted medals table and select specific columns to avoid ambiguity
    main_df = main_df.join(medals, "medal_id", "left") \
        .withColumn("medal_name", F.col("medals.name")) \
        .drop("medals.name")

    # Join with broadcasted maps table and select specific columns
    main_df = main_df.join(maps, "mapid", "inner") \
        .withColumn("map_name", F.col("maps.name")) \
        .drop("maps.name")

    # Cache the main dataframe since we'll use it multiple times
    main_df.cache()

    print("=== Analysis Results ===\n")

    # 1. Which player averages the most kills per game?
    print("1. Player with highest average kills per game:")
    avg_kills_per_player = main_df \
        .groupBy("player_gamertag") \
        .agg(
        F.avg("player_total_kills").alias("avg_kills_per_game"),
        F.count("match_id").alias("games_played")
    ) \
        .filter(F.col("games_played") >= 5) \
        .orderBy(F.desc("avg_kills_per_game"))

    avg_kills_per_player.show(10)

    # 2. Which playlist gets played the most?
    print("\n2. Most played playlist:")
    most_played_playlist = main_df \
        .groupBy("playlist_id") \
        .agg(F.countDistinct("match_id").alias("matches_played")) \
        .orderBy(F.desc("matches_played"))

    most_played_playlist.show(10)

    # 3. Which map gets played the most?
    print("\n3. Most played map:")
    most_played_map = main_df \
        .groupBy("mapid", "map_name") \
        .agg(F.countDistinct("match_id").alias("matches_played")) \
        .orderBy(F.desc("matches_played"))

    most_played_map.show(10)

    # 4. Which map do players get the most Killing Spree medals on?
    print("\n4. Map with most Killing Spree medals:")
    killing_spree_by_map = main_df \
        .filter(F.col("medal_name") == "Killing Spree") \
        .groupBy("mapid", "map_name") \
        .agg(F.count("*").alias("killing_spree_medals")) \
        .orderBy(F.desc("killing_spree_medals"))

    killing_spree_by_map.show(10)

    return main_df


def test_sort_within_partitions(main_df):
    """Test different sortWithinPartitions strategies"""

    print("\n=== Testing sortWithinPartitions Strategies ===\n")

    # Create aggregated dataset for testing
    aggregated_df = main_df \
        .groupBy("playlist_id", "mapid", "player_gamertag") \
        .agg(
        F.sum("player_total_kills").alias("total_kills"),
        F.count("match_id").alias("games_played"),
        F.avg("player_total_kills").alias("avg_kills")
    )

    # Test 1: Sort by playlist_id (low cardinality)
    print("Testing sort by playlist_id...")
    df_sorted_playlist = aggregated_df.sortWithinPartitions("playlist_id")
    df_sorted_playlist.write.mode("overwrite").parquet("output/sorted_by_playlist")

    # Test 2: Sort by mapid (low cardinality)
    print("Testing sort by mapid...")
    df_sorted_map = aggregated_df.sortWithinPartitions("mapid")
    df_sorted_map.write.mode("overwrite").parquet("output/sorted_by_map")

    # Test 3: Sort by both playlist and map (both low cardinality)
    print("Testing sort by playlist_id and mapid...")
    df_sorted_both = aggregated_df.sortWithinPartitions("playlist_id", "mapid")
    df_sorted_both.write.mode("overwrite").parquet("output/sorted_by_playlist_map")

    # Test 4: Sort by player_gamertag (high cardinality - for comparison)
    print("Testing sort by player_gamertag...")
    df_sorted_player = aggregated_df.sortWithinPartitions("player_gamertag")
    df_sorted_player.write.mode("overwrite").parquet("output/sorted_by_player")

    print("Sorting tests completed. Check the output folder sizes to compare compression effectiveness.")


def main():
    """Main execution function"""
    # Create Spark session
    spark = create_spark_session()

    try:
        print("Loading and bucketing tables...")
        tables = load_and_bucket_tables(spark)

        print("Performing analysis...")
        main_df = perform_analysis(tables)

        print("Testing sort within partitions...")
        test_sort_within_partitions(main_df)

        print("\nJob completed successfully!")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise

    finally:
        spark.stop()


if __name__ == "__main__":
    main()