from pyspark.sql import SparkSession
import pyspark.sql.functions as F

# Initialize Spark
spark = SparkSession.builder \
    .appName("GamingAnalysisHomework_Fixed") \
    .config("spark.sql.shuffle.partitions", "16") \
    .getOrCreate()

# Load data - adjust paths as needed
base_path = "../../data"

tables = {
    "match_details": spark.read.option("header", "true").option("inferSchema", "true").csv(
        f"{base_path}/match_details.csv"),
    "matches": spark.read.option("header", "true").option("inferSchema", "true").csv(f"{base_path}/matches.csv"),
    "medals": spark.read.option("header", "true").option("inferSchema", "true").csv(f"{base_path}/medals.csv"),
    "maps": spark.read.option("header", "true").option("inferSchema", "true").csv(f"{base_path}/maps.csv"),
    "medals_matches_players": spark.read.option("header", "true").option("inferSchema", "true").csv(
        f"{base_path}/medals_matches_players.csv")
}

print("Data loaded successfully!")
for name, df in tables.items():
    print(f"{name}: {df.count()} rows")

# ============================================================================
# Query 1: Disabled automatic broadcast joins
# ============================================================================
print("\n=== Query 1: Disabled automatic broadcast joins ===")
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
spark.conf.set("spark.sql.adaptive.autoBroadcastJoinThreshold", "-1")  # For AQE compatibility

main_df_no_broadcast = tables["match_details"] \
    .join(tables["matches"], "match_id", "inner") \
    .join(tables["medals_matches_players"], ["match_id", "player_gamertag"], "left") \
    .join(tables["medals"], "medal_id", "left") \
    .join(tables["maps"], "mapid", "inner")

result_no_broadcast = main_df_no_broadcast.groupBy("playlist_id") \
    .agg(F.countDistinct("match_id").alias("total_matches")) \
    .orderBy(F.desc("total_matches"))

print("Top playlists by match count (no broadcast):")
result_no_broadcast.show()

# ============================================================================
# Query 2: Broadcast join
# ============================================================================
print("\n=== Query 2: Broadcast join ===")

# Pre-rename columns to avoid ambiguity
medals_broadcast = F.broadcast(
    tables["medals"].select(
        F.col("medal_id"),
        F.col("name").alias("medal_name"),
        F.col("description").alias("medal_description")
    )
)

maps_broadcast = F.broadcast(
    tables["maps"].select(
        F.col("mapid"),
        F.col("name").alias("map_name")
    )
)

main_df_broadcast = tables["match_details"] \
    .join(tables["matches"], "match_id", "inner") \
    .join(tables["medals_matches_players"], ["match_id", "player_gamertag"], "left") \
    .join(medals_broadcast, "medal_id", "left") \
    .join(maps_broadcast, "mapid", "inner")

result_broadcast = main_df_broadcast.groupBy("playlist_id") \
    .agg(F.countDistinct("match_id").alias("total_matches")) \
    .orderBy(F.desc("total_matches"))

print("Top playlists by match count (with broadcast):")
result_broadcast.show()

# ============================================================================
# Query 3: Bucket join
# ============================================================================
print("\n=== Query 3: Bucket join ===")

# Enable bucketing
spark.conf.set("spark.sql.bucketing.enabled", "true")

# Write bucketed tables to catalog
tables["match_details"].write.mode("overwrite").bucketBy(16, "match_id").sortBy("match_id").saveAsTable("md_bucketed")
tables["matches"].write.mode("overwrite").bucketBy(16, "match_id").sortBy("match_id").saveAsTable("m_bucketed")
tables["medals_matches_players"].write.mode("overwrite").bucketBy(16, "match_id").sortBy("match_id").saveAsTable(
    "mmp_bucketed")

# Read back the bucketed tables
md_bucketed = spark.table("md_bucketed")
m_bucketed = spark.table("m_bucketed")
mmp_bucketed = spark.table("mmp_bucketed")

# Perform the bucket join
main_df_bucketed = md_bucketed.join(m_bucketed, "match_id", "inner") \
    .join(mmp_bucketed, ["match_id", "player_gamertag"], "left") \
    .join(medals_broadcast, "medal_id", "left") \
    .join(maps_broadcast, "mapid", "inner")

result_bucketed = main_df_bucketed.groupBy("playlist_id") \
    .agg(F.countDistinct("match_id").alias("total_matches")) \
    .orderBy(F.desc("total_matches"))

print("Top playlists by match count (bucketed join):")
result_bucketed.show()

print("Execution plan for bucketed join:")
main_df_bucketed.explain("formatted")

# ============================================================================
# Query 4a: Player with highest average kills per game (FIXED)
# ============================================================================
print("\n=== Query 4a: Player with highest average kills per game ===")

# Calculate from match_details alone to avoid duplication
md = tables["match_details"]
avg_kills_per_player = md.groupBy("player_gamertag") \
    .agg(
    F.avg("player_total_kills").alias("avg_kills_per_game"),
    F.countDistinct("match_id").alias("games_played")
) \
    .orderBy(F.desc("avg_kills_per_game"))

print("Top 10 players by average kills per game:")
avg_kills_per_player.show(10)

# ============================================================================
# Query 4b: Playlist with the most Killing Spree medals
# ============================================================================
print("\n=== Query 4b: Playlist with the most Killing Spree medals ===")

killing_spree_by_playlist = main_df_broadcast \
    .filter(F.col("medal_name") == "Killing Spree") \
    .groupBy("playlist_id") \
    .agg(F.countDistinct("match_id").alias("matches_with_killing_spree")) \
    .orderBy(F.desc("matches_with_killing_spree"))

print("Playlists with most Killing Spree medals:")
killing_spree_by_playlist.show()

# ============================================================================
# Query 4c: Which player has the most Killing Spree medals
# ============================================================================
print("\n=== Query 4c: Player with the most Killing Spree medals ===")

killing_spree_by_player = main_df_broadcast \
    .filter(F.col("medal_name") == "Killing Spree") \
    .groupBy("player_gamertag") \
    .agg(F.countDistinct("match_id").alias("matches_with_killing_spree")) \
    .orderBy(F.desc("matches_with_killing_spree"))

print("Players with most Killing Spree medals:")
killing_spree_by_player.show(10)

# ============================================================================
# Query 4d: Which map has the most Killing Spree medals
# ============================================================================
print("\n=== Query 4d: Map with the most Killing Spree medals ===")

killing_spree_by_map = main_df_broadcast \
    .filter(F.col("medal_name") == "Killing Spree") \
    .groupBy("map_name") \
    .agg(F.count("*").alias("killing_spree_medals")) \
    .orderBy(F.desc("killing_spree_medals"))

print("Maps with most Killing Spree medals:")
killing_spree_by_map.show()

# ============================================================================
# Query 5: Compare sortWithinPartitions with different partitioning strategies
# ============================================================================
print("\n=== Query 5: Partitioning + sortWithinPartitions ===")

# Create aggregated data for partitioning
aggregated_df = main_df_broadcast.groupBy("playlist_id", "mapid", "player_gamertag") \
    .agg(
    F.sum("player_total_kills").alias("total_kills"),
    F.countDistinct("match_id").alias("games_played"),
    F.avg("player_total_kills").alias("avg_kills")
)

# Version A: partition by playlist_id
print("Writing Version A: partitioned by playlist_id")
aggregated_df.sortWithinPartitions("playlist_id") \
    .write.mode("overwrite").partitionBy("playlist_id") \
    .parquet("output/part_by_playlist")

# Version B: partition by mapid
print("Writing Version B: partitioned by mapid")
aggregated_df.sortWithinPartitions("mapid") \
    .write.mode("overwrite").partitionBy("mapid") \
    .parquet("output/part_by_map")

# Version C: partition by both playlist_id and mapid
print("Writing Version C: partitioned by playlist_id and mapid")
aggregated_df.sortWithinPartitions("playlist_id", "mapid") \
    .write.mode("overwrite").partitionBy("playlist_id", "mapid") \
    .parquet("output/part_by_playlist_map")

# Compare sizes
try:
    fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())


    def dir_size(path):
        return fs.getContentSummary(spark._jvm.org.apache.hadoop.fs.Path(path)).getLength()


    print(f"Version A size: {dir_size('output/part_by_playlist')} bytes")
    print(f"Version B size: {dir_size('output/part_by_map')} bytes")
    print(f"Version C size: {dir_size('output/part_by_playlist_map')} bytes")
except Exception as e:
    print(f"Could not calculate sizes: {e}")
    print("Check sizes manually in the output directory")

# Clean up
try:
    spark.catalog.dropTempView("md_bucketed")
    spark.catalog.dropTempView("m_bucketed")
    spark.catalog.dropTempView("mmp_bucketed")
except:
    pass  # Views might not exist

print("\n=== Analysis Complete ===")
spark.stop()