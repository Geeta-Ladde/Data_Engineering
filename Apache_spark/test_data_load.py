#!/usr/bin/env python3
"""
Step 1: Test ONLY data loading
Save this as test_data_loading.py and run it first
"""

from pyspark.sql import SparkSession
import os

# Initialize Spark
spark = SparkSession.builder \
    .appName("TestDataLoading") \
    .getOrCreate()

# IMPORTANT: Update this path to match where your CSV files are located
base_path = "../../data"  # Change this to your actual data path!

print(f"Testing data loading from: {base_path}")
print("-" * 50)

# Test each file individually
files_to_test = {
    "match_details": f"{base_path}/match_details.csv",
    "matches": f"{base_path}/matches.csv",
    "medals": f"{base_path}/medals.csv",
    "maps": f"{base_path}/maps.csv",
    "medals_matches_players": f"{base_path}/medals_matches_players.csv"
}

tables = {}
all_success = True

for name, path in files_to_test.items():
    try:
        print(f"Loading {name}...")
        if not os.path.exists(path):
            print(f"❌ FILE NOT FOUND: {path}")
            all_success = False
            continue

        df = spark.read.option("header", "true").option("inferSchema", "true").csv(path)
        count = df.count()
        tables[name] = df

        print(f"✅ {name}: {count} rows loaded")

        # Show first few rows and schema
        print(f"   Schema: {len(df.columns)} columns")
        print(f"   Columns: {df.columns}")

    except Exception as e:
        print(f"❌ Error loading {name}: {str(e)}")
        all_success = False

print("-" * 50)
if all_success:
    print("🎉 ALL DATA FILES LOADED SUCCESSFULLY!")
    print("You can now test individual queries.")
else:
    print("⚠️  DATA LOADING FAILED!")
    print("Fix the data paths before testing queries.")

spark.stop()