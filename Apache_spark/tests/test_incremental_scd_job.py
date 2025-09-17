# test_incremental_scd_job.py
# Fixed tests for the incremental SCD PySpark job

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, BooleanType, IntegerType
import tempfile
import shutil
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jobs.incremental_scd_job import run_incremental_scd_job

class TestIncrementalSCDJob:

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
            .appName("TestIncrementalSCDJob") \
            .master("local[1]") \
            .config("spark.sql.warehouse.dir", tempfile.mkdtemp()) \
            .getOrCreate()

        # Create temporary directories for test data
        cls.temp_dir = tempfile.mkdtemp()
        cls.players_scd_path = os.path.join(cls.temp_dir, "players_scd")
        cls.players_path = os.path.join(cls.temp_dir, "players")
        cls.output_path = os.path.join(cls.temp_dir, "output")

        # Define schemas
        cls.players_scd_schema = StructType([
            StructField("player_name", StringType(), True),
            StructField("scoring_class", StringType(), True),
            StructField("is_active", BooleanType(), True),
            StructField("start_season", IntegerType(), True),
            StructField("end_season", IntegerType(), True),
            StructField("current_season", IntegerType(), True)
        ])

        cls.players_schema = StructType([
            StructField("player_name", StringType(), True),
            StructField("scoring_class", StringType(), True),
            StructField("is_active", BooleanType(), True),
            StructField("current_season", IntegerType(), True)
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

    def run_scd_job_direct(self, scd_data, players_data):
        """
        Helper method to run SCD logic directly without file I/O
        This uses the UPDATED SQL query with null-safe comparisons and dropped players
        """
        # Create DataFrames
        players_scd_df = self.spark.createDataFrame(scd_data, self.players_scd_schema)
        players_df = self.spark.createDataFrame(players_data, self.players_schema)

        # Register as temporary views
        players_scd_df.createOrReplaceTempView("players_scd")
        players_df.createOrReplaceTempView("players")

        # Execute the FIXED SCD query with null-safe comparisons and dropped players
        result = self.spark.sql("""
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
                SELECT * FROM players
                WHERE current_season = 2022
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
                    2022 AS start_season,
                    2022 AS end_season
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
                    2022 AS start_season,
                    2022 AS end_season
                FROM this_season_data ts
                LEFT JOIN last_season_scd ls
                ON ts.player_name = ts.player_name
                WHERE ls.player_name IS NULL
            ),
            -- NEW: Handle dropped players (existed in 2021, missing in 2022)
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
            SELECT *, 2022 AS current_season FROM (
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

        return result.collect()

    def test_unchanged_players_extend_season(self):
        """Test that unchanged players get their end_season extended"""

        # Create fake SCD input data
        scd_data = [
            ("LeBron James", "star", True, 2020, 2021, 2021),
            ("Kevin Durant", "star", True, 2019, 2021, 2021)
        ]

        # Create fake current season data (no changes)
        players_data = [
            ("LeBron James", "star", True, 2022),
            ("Kevin Durant", "star", True, 2022)
        ]

        # Run the SCD logic
        result_list = self.run_scd_job_direct(scd_data, players_data)

        # Verify unchanged records exist and have updated end_season
        unchanged_records = [r for r in result_list if r.end_season == 2022]
        assert len(unchanged_records) == 2

        # Verify LeBron's record
        lebron = [r for r in result_list if r.player_name == "LeBron James"][0]
        assert lebron.start_season == 2020  # Preserved
        assert lebron.end_season == 2022  # Extended

    def test_changed_players_create_new_records(self):
        """Test that changed players get old record closed and new record created"""

        # Create SCD data with one player
        scd_data = [
            ("Steph Curry", "star", True, 2020, 2021, 2021)
        ]

        # Player changed scoring class
        players_data = [
            ("Steph Curry", "good", True, 2022)  # Changed from "star" to "good"
        ]

        # Run the SCD logic
        result_list = self.run_scd_job_direct(scd_data, players_data)

        # Should have 2 records for Steph (old closed, new created)
        steph_records = [r for r in result_list if r.player_name == "Steph Curry"]
        assert len(steph_records) == 2

        # Verify old record (closed)
        old_record = [r for r in steph_records if r.scoring_class == "star"][0]
        assert old_record.end_season == 2021

        # Verify new record
        new_record = [r for r in steph_records if r.scoring_class == "good"][0]
        assert new_record.start_season == 2022
        assert new_record.end_season == 2022

    def test_new_players_get_initial_records(self):
        """Test that completely new players get new records created"""

        # Empty SCD table
        scd_data = []

        # New player
        players_data = [
            ("Rookie Smith", "average", True, 2022)
        ]

        # Run the SCD logic
        result_list = self.run_scd_job_direct(scd_data, players_data)

        # Should have 1 record for new player
        assert len(result_list) == 1
        rookie = result_list[0]
        assert rookie.player_name == "Rookie Smith"
        assert rookie.start_season == 2022
        assert rookie.end_season == 2022
        assert rookie.current_season == 2022

    def test_historical_records_preserved(self):
        """Test that historical records (end_season < last_season) are preserved"""

        # SCD data with historical and current records
        scd_data = [
            ("Retired Player", "good", False, 2018, 2020, 2021),  # Historical
            ("Active Player", "star", True, 2020, 2021, 2021)  # Current
        ]

        # Only active player continues
        players_data = [
            ("Active Player", "star", True, 2022)
        ]

        # Run the SCD logic
        result_list = self.run_scd_job_direct(scd_data, players_data)

        # Should have historical record preserved
        retired_records = [r for r in result_list if r.player_name == "Retired Player"]
        assert len(retired_records) == 1
        assert retired_records[0].end_season == 2020  # Unchanged

        # Should have active player record extended
        active_records = [r for r in result_list if r.player_name == "Active Player"]
        assert len(active_records) == 1
        assert active_records[0].end_season == 2022  # Extended

    def test_dropped_players_preserved(self):
        """Test that players who existed in 2021 but missing in 2022 are preserved as closed records"""

        # Player existed in 2021
        scd_data = [
            ("Retired Player", "good", True, 2020, 2021, 2021)
        ]

        # Player doesn't appear in 2022 (retired/dropped)
        players_data = []  # Empty - no one plays in 2022

        result_list = self.run_scd_job_direct(scd_data, players_data)

        # Should still have the retired player's record preserved
        assert len(result_list) == 1
        retired_record = result_list[0]
        assert retired_record.player_name == "Retired Player"
        assert retired_record.end_season == 2021  # Stays closed at 2021
        assert retired_record.current_season == 2022  # But appears in 2022 snapshot

    def test_null_safe_comparisons(self):
        """Test that null-safe comparisons work correctly"""

        # Player with NULL scoring_class in 2021
        scd_data = [
            ("Null Player", None, True, 2020, 2021, 2021)
        ]

        # Player still has NULL scoring_class in 2022 (should be unchanged)
        players_data = [
            ("Null Player", None, True, 2022)
        ]

        result_list = self.run_scd_job_direct(scd_data, players_data)

        # Should have 1 record (unchanged, so end_season extended to 2022)
        assert len(result_list) == 1
        null_record = result_list[0]
        assert null_record.player_name == "Null Player"
        assert null_record.scoring_class is None
        assert null_record.end_season == 2022  # Extended because no change detected

    def test_scd_job_end_to_end(self):
        """Test the actual SCD job function with file I/O - END TO END TEST"""

        # Create test input data
        scd_data = [
            ("Test Player", "good", True, 2020, 2021, 2021)
        ]
        players_data = [
            ("Test Player", "star", True, 2022)  # Changed class
        ]

        # Write test data to parquet files
        scd_df = self.spark.createDataFrame(scd_data, self.players_scd_schema)
        players_df = self.spark.createDataFrame(players_data, self.players_schema)

        scd_df.write.mode("overwrite").parquet(self.players_scd_path)
        players_df.write.mode("overwrite").parquet(self.players_path)

        # Run the job with the correct parameters
        run_incremental_scd_job(
            last_scd_path=self.players_scd_path,
            current_season_path=self.players_path,
            output_path=self.output_path,
            previous_season=2021,
            current_season=2022
        )

        # Read the output and verify
        result_df = self.spark.read.parquet(self.output_path)
        result_list = result_df.collect()

        # Should have 2 records (old closed, new opened)
        assert len(result_list) == 2

        # Verify the change was detected
        test_records = [r for r in result_list if r.player_name == "Test Player"]
        assert len(test_records) == 2

        # Check old record (closed)
        old_record = [r for r in test_records if r.scoring_class == "good"][0]
        assert old_record.end_season == 2021

        # Check new record
        new_record = [r for r in test_records if r.scoring_class == "star"][0]
        assert new_record.start_season == 2022
        assert new_record.end_season == 2022
        assert new_record.current_season == 2022


if __name__ == "__main__":
    pytest.main([__file__])