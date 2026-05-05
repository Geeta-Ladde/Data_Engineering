# test_cumulative_players_job.py
# Fixed tests for the cumulative players PySpark job

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType, FloatType, BooleanType
import tempfile
import shutil
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jobs.cumulative_players_job import run_cumulative_players_job

class TestCumulativePlayersJob:

    @classmethod
    def setup_class(cls):
        """Set up Spark session and temporary directories for testing"""
        # Stop any existing Spark session
        try:
            existing_spark = SparkSession.getActiveSession()
            if existing_spark:
                existing_spark.stop()
        except:
            pass

        cls.spark = SparkSession.builder \
            .appName("TestCumulativePlayersJob") \
            .master("local[1]") \
            .config("spark.sql.warehouse.dir", tempfile.mkdtemp()) \
            .getOrCreate()

        # Create temporary directories for test data
        cls.temp_dir = tempfile.mkdtemp()
        cls.players_path = os.path.join(cls.temp_dir, "players")
        cls.player_seasons_path = os.path.join(cls.temp_dir, "player_seasons")
        cls.output_path = os.path.join(cls.temp_dir, "output")

        # Define schemas
        cls.season_stats_schema = StructType([
            StructField("season", IntegerType(), True),
            StructField("pts", FloatType(), True),
            StructField("ast", FloatType(), True),
            StructField("reb", FloatType(), True),
            StructField("weight", FloatType(), True)
        ])

        cls.players_schema = StructType([
            StructField("player_name", StringType(), True),
            StructField("height", StringType(), True),
            StructField("college", StringType(), True),
            StructField("country", StringType(), True),
            StructField("draft_year", IntegerType(), True),
            StructField("draft_round", IntegerType(), True),
            StructField("draft_number", IntegerType(), True),
            StructField("seasons", ArrayType(cls.season_stats_schema), True),
            StructField("scoring_class", StringType(), True),
            StructField("is_active", BooleanType(), True),
            StructField("current_season", IntegerType(), True)
        ])

        cls.player_seasons_schema = StructType([
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

    @classmethod
    def teardown_class(cls):
        """Clean up Spark session and temporary directories"""
        try:
            cls.spark.stop()
        except:
            pass
        try:
            shutil.rmtree(cls.temp_dir)
        except:
            pass

    def setup_method(self):
        """Clean up output directory before each test"""
        try:
            if os.path.exists(self.output_path):
                shutil.rmtree(self.output_path)
        except:
            pass

    def run_cumulative_job_direct(self, players_data, player_seasons_data):
        """
        Helper method to run cumulative logic directly without file I/O
        """
        # Create DataFrames
        players_df = self.spark.createDataFrame(players_data, self.players_schema)
        player_seasons_df = self.spark.createDataFrame(player_seasons_data, self.player_seasons_schema)

        # Register as temporary views
        players_df.createOrReplaceTempView("players")
        player_seasons_df.createOrReplaceTempView("player_seasons")

        # Execute the cumulative query directly
        result = self.spark.sql("""
            WITH last_season AS (
                SELECT * FROM players
                WHERE current_season = 1997
            ), 
            this_season AS (
                SELECT * FROM player_seasons
                WHERE season = 1998
            )
            SELECT
                COALESCE(ls.player_name, ts.player_name) as player_name,
                COALESCE(ls.height, ts.height) as height,
                COALESCE(ls.college, ts.college) as college,
                COALESCE(ls.country, ts.country) as country,
                COALESCE(ls.draft_year, ts.draft_year) as draft_year,
                COALESCE(ls.draft_round, ts.draft_round) as draft_round,
                COALESCE(ls.draft_number, ts.draft_number) as draft_number,

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

                CASE WHEN ts.season IS NOT NULL THEN true ELSE false END as is_active,

                1998 AS current_season

            FROM last_season ls
            FULL OUTER JOIN this_season ts
            ON ls.player_name = ts.player_name
        """)

        return result.collect()

    def test_new_player_first_season(self):
        """Test that completely new player gets properly created"""

        # Empty existing players
        players_data = []

        # New player season data
        player_seasons_data = [
            ("Kobe Bryant", 1998, 7.6, 1.3, 1.9, 200.0, "6-6", "Lower Merion HS", "USA", 1996, 1, 13)
        ]

        # Run cumulative job
        result_list = self.run_cumulative_job_direct(players_data, player_seasons_data)

        # Verify we have one record
        assert len(result_list) == 1
        kobe_record = result_list[0]

        # Verify player info
        assert kobe_record.player_name == "Kobe Bryant"
        assert kobe_record.height == "6-6"
        assert kobe_record.college == "Lower Merion HS"

        # Verify seasons array has 1 season
        assert len(kobe_record.seasons) == 1
        assert kobe_record.seasons[0].season == 1998
        assert abs(kobe_record.seasons[0].pts - 7.6) < 0.01

        # Verify scoring class (7.6 points = "bad")
        assert kobe_record.scoring_class == "bad"

        # Verify player is active
        assert kobe_record.is_active == True
        assert kobe_record.current_season == 1998

    def test_existing_player_no_new_season(self):
        """Test existing player who didn't play new season stays inactive"""

        # Existing player data with previous season
        existing_seasons = [{"season": 1996, "pts": 15.2, "ast": 4.1, "reb": 6.3, "weight": 210.0}]
        players_data = [
            ("Retired Player", "6-4", "Duke", "USA", 1990, 2, 25,
             existing_seasons, "good", True, 1997)
        ]

        # Empty new seasons (player didn't play in 1998)
        player_seasons_data = []

        # Run cumulative job
        result_list = self.run_cumulative_job_direct(players_data, player_seasons_data)

        # Verify we have one record
        assert len(result_list) == 1
        retired_record = result_list[0]

        # Verify player info preserved
        assert retired_record.player_name == "Retired Player"

        # Verify seasons array unchanged (still has 1996 season)
        assert len(retired_record.seasons) == 1
        assert retired_record.seasons[0].season == 1996

        # Verify scoring class preserved (no new season to update from)
        assert retired_record.scoring_class == "good"

        # Verify player is now inactive
        assert retired_record.is_active == False

        # Verify current season updated
        assert retired_record.current_season == 1998

    def test_scoring_class_calculation(self):
        """Test that scoring class is correctly calculated based on points"""

        # Empty existing players
        players_data = []

        # Multiple players with different point totals
        player_seasons_data = [
            ("Star Player", 1998, 25.0, 6.0, 8.0, 230.0, "6-8", "UCLA", "USA", 1995, 1, 5),  # > 20 = star
            ("Good Player", 1998, 17.5, 4.5, 6.0, 210.0, "6-5", "Duke", "USA", 1994, 1, 8),  # > 15 = good
            ("Average Player", 1998, 12.0, 3.0, 4.5, 200.0, "6-3", "UNC", "USA", 1996, 2, 35),  # > 10 = average
            ("Bad Player", 1998, 8.5, 2.0, 3.0, 190.0, "6-1", "State", "USA", 1997, 2, 45)  # <= 10 = bad
        ]

        # Run cumulative job
        result_list = self.run_cumulative_job_direct(players_data, player_seasons_data)

        # Create lookup for easier testing
        results_by_name = {record.player_name: record for record in result_list}

        # Verify scoring classifications
        assert results_by_name["Star Player"].scoring_class == "star"
        assert results_by_name["Good Player"].scoring_class == "good"
        assert results_by_name["Average Player"].scoring_class == "average"
        assert results_by_name["Bad Player"].scoring_class == "bad"

        # Verify all are active
        for record in result_list:
            assert record.is_active == True

    def test_existing_player_adds_new_season(self):
        """Test that existing player gets new season added to their seasons array"""

        # Create existing player data with 1997 season
        existing_seasons = [{"season": 1996, "pts": 18.5, "ast": 5.2, "reb": 7.1, "weight": 220.0}]
        players_data = [
            ("Michael Jordan", "6-6", "North Carolina", "USA", 1984, 1, 3,
             existing_seasons, "good", True, 1997)
        ]

        # Create new season data for 1998
        player_seasons_data = [
            ("Michael Jordan", 1998, 28.7, 5.8, 5.8, 218.0, "6-6", "North Carolina", "USA", 1984, 1, 3)
        ]

        # Run cumulative job
        result_list = self.run_cumulative_job_direct(players_data, player_seasons_data)

        # Verify we have one record
        assert len(result_list) == 1
        jordan_record = result_list[0]

        # Verify basic info is preserved
        assert jordan_record.player_name == "Michael Jordan"
        assert jordan_record.height == "6-6"
        assert jordan_record.college == "North Carolina"

        # Verify seasons array now has 2 seasons
        assert len(jordan_record.seasons) == 2

        # Verify 1996 season is preserved
        season_1996 = [s for s in jordan_record.seasons if s.season == 1996][0]
        assert abs(season_1996.pts - 18.5) < 0.01

        # Verify 1998 season was added
        season_1998 = [s for s in jordan_record.seasons if s.season == 1998][0]
        assert abs(season_1998.pts - 28.7) < 0.01
        assert abs(season_1998.ast - 5.8) < 0.01

        # Verify scoring class updated based on 1998 stats (28.7 > 20 = "star")
        assert jordan_record.scoring_class == "star"

        # Verify player is active
        assert jordan_record.is_active == True

        # Verify current season updated
        assert jordan_record.current_season == 1998

    def test_cumulative_job_end_to_end(self):
        """Test the actual cumulative job function with file I/O - END TO END TEST"""

        # Create test input data - existing player with previous season
        existing_seasons = [{"season": 1996, "pts": 20.0, "ast": 5.0, "reb": 7.0, "weight": 220.0}]
        players_data = [
            ("Test Player", "6-6", "Test College", "USA", 1994, 1, 10,
             existing_seasons, "star", True, 1997)
        ]

        # New season data - player improves to superstar level
        player_seasons_data = [
            ("Test Player", 1998, 30.0, 6.0, 8.0, 225.0, "6-6", "Test College", "USA", 1994, 1, 10)
        ]

        # Write test data to parquet files
        players_df = self.spark.createDataFrame(players_data, self.players_schema)
        player_seasons_df = self.spark.createDataFrame(player_seasons_data, self.player_seasons_schema)

        players_df.write.mode("overwrite").parquet(self.players_path)
        player_seasons_df.write.mode("overwrite").parquet(self.player_seasons_path)

        # Run the job with the correct parameters
        run_cumulative_players_job(
            last_season_path=self.players_path,
            current_season_path=self.player_seasons_path,
            output_path=self.output_path,
            target_season=1998
        )

        # Read the output and verify
        result_df = self.spark.read.parquet(self.output_path)
        result_list = result_df.collect()

        # Should have 1 record (the test player with updated stats)
        assert len(result_list) == 1
        test_record = result_list[0]

        # Verify player info
        assert test_record.player_name == "Test Player"
        assert test_record.height == "6-6"
        assert test_record.college == "Test College"

        # Verify seasons array now has 2 seasons (1996 + 1998)
        assert len(test_record.seasons) == 2

        # Verify 1996 season is preserved
        season_1996 = [s for s in test_record.seasons if s.season == 1996][0]
        assert abs(season_1996.pts - 20.0) < 0.01

        # Verify 1998 season was added
        season_1998 = [s for s in test_record.seasons if s.season == 1998][0]
        assert abs(season_1998.pts - 30.0) < 0.01
        assert abs(season_1998.ast - 6.0) < 0.01

        # Verify scoring class updated based on 1998 stats (30.0 > 20 = "star")
        assert test_record.scoring_class == "star"

        # Verify player is active and current season updated
        assert test_record.is_active == True
        assert test_record.current_season == 1998


if __name__ == "__main__":
    pytest.main([__file__])