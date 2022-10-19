#!/usr/bin/env python3

# make_database.py write to results.csv and results.sqlite3

import os
import re
import sys
import sqlite3

sys.path.insert(0, os.getcwd())
from helpers import create_fedora_results_table, recursive_find


print("⭐️ Reading in experiments...")
experiments = list(recursive_find("artifacts/results/extracted/fedora", "*.json"))
df = create_fedora_results_table(experiments)

# Export as csv
print("⭐️ Exporting dataframe as results.csv")
df.original = df.original.apply(lambda s: re.sub(r"^(first|second)", "", s, 1))
df.original = df.original.apply(lambda s: re.sub(r"^/lib/", "/usr/lib/", s, 1))
df.original = df.original.apply(lambda s: re.sub(r"^/lib64/", "/usr/lib64/", s, 1))
df.changed = df.changed.apply(lambda s: re.sub(r"^(first|second)", "", s, 1))
df.changed = df.changed.apply(lambda s: re.sub(r"^/lib/", "/usr/lib/", s, 1))
df.changed = df.changed.apply(lambda s: re.sub(r"^/lib64/", "/usr/lib64/", s, 1))
df.to_csv("results.csv", index=False, header=False)

# Rename seconds to time
df = df.rename({"seconds": "time"}, axis=1)

# We don't need size columns
df = df.drop(["size_original", "size_changed"], axis=1)

# Read in results.csv and write to sqlite from pandas directly
print("⭐️ Writing database results.sqlite3...")
database = "results.sqlite3"

# Clean up previous database
if os.path.exists(database):
    print("Cleaning up previously written results.sqlite3")
    os.remove(database)

with sqlite3.connect(database) as conn:

    # Create original database with pandas
    df.to_sql(name="results", con=conn, if_exists="replace", index=False)

    # Apply operations!
    with open("make_results_table.sql", "r") as fd:
        conn.executescript(fd.read())
