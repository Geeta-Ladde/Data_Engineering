#!/usr/bin/env python3
"""
Test file for src/tests/ folder
Save this as test_homework.py in: src/tests/
"""

from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import os

# Initialize Spark
spark = SparkSession.builder \
    .appName("HomeworkTest") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

# Path from src/tests/ to data folder
# src/tests/ -> src/ -> 3-spark-fundamentals/ -> data/
base_path = "../../data"

print("Testing homework from tests folder...")
print(f"Current directory: {os.getcwd()}")
print(f"Looking for data in: {base_path}")
print("-" * 60)


def test_data_loading():
    """Test that all CSV files can be loaded"""
    print("TEST 1: Data Loading")

    files_to_test = [
        "match_details.csv",
        "matches.csv",
        "medals.csv",
        "maps.csv",
        "medals_matches_players.csv"
    ]

    tables = {}
    all_loaded = True

    for file_name in files_to_test:
        try:
            file_path = f"{base_path}/{file_name}"
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                all_loaded = False
                continue

            df = spark.read.option("header", "true").option("inferSchema", "true").csv(file_path)
            count = df.count()
            tables[file_name.replace('.csv', '')] = df
            print(f"✅ {file_name}: {count} rows")

        except Exception as e:
            print(f"❌ Error loading {file_name}: {e}")
            all_loaded = False

    return tables if all_loaded else None


def test_basic_join():
    """Test basic joins work"""
    print("\nTEST 2: Basic Join")

    tables = test_data_loading()
    if not tables:
        print("❌ Cannot test joins - data loading failed")
        return False

    try:
        # Simple join test
        result_df = tables['match_details'].join(tables['matches'], "match_id", "inner")
        count = result_df.count()
        print(f"✅ Basic join successful: {count} rows after join")
        return True

    except Exception as e:
        print(f"❌ Join failed: {e}")
        return False


def test_aggregation():
    """Test basic aggregation works"""
    print("\nTEST 3: Basic Aggregation")

    try:
        tables = {}
        tables['match_details'] = spark.read.option("header", "true").option("inferSchema", "true").csv(
            f"{base_path}/match_details.csv")

        result = tables['match_details'].groupBy("player_gamertag") \
            .agg(F.avg("player_total_kills").alias("avg_kills")) \
            .orderBy(F.desc("avg_kills")) \
            .limit(3)

        rows = result.collect()
        print(f"✅ Aggregation successful: Top player has {rows[0]['avg_kills']:.2f} avg kills")
        return True

    except Exception as e:
        print(f"❌ Aggregation failed: {e}")
        return False


# Run all tests
def main():
    test_results = []

    test_results.append(test_data_loading() is not None)
    test_results.append(test_basic_join())
    test_results.append(test_aggregation())

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(test_results)
    total = len(test_results)

    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {passed / total * 100:.1f}%")

    if passed == total:
        print("🎉 ALL BASIC TESTS PASSED!")
        print("Your data loading and basic operations work.")
        print("Now you can test your full homework file.")
    else:
        print("⚠️  Some basic tests failed.")
        print("Fix these issues before testing your homework.")

    spark.stop()


if __name__ == "__main__":
    main()