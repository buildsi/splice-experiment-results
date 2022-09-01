import pandas
import sys
import os
import json
sys.path.insert(0, os.getcwd())
from helpers import recursive_find, read_json, create_fedora_results_table

experiments = list(recursive_find("artifacts/results/extracted/fedora", "*.json"))
df = create_fedora_results_table(experiments)
# Export as csv
import re
df.original = df.original.apply(lambda s: re.sub(r"^(first|second)", "", s, 1))
df.original = df.original.apply(lambda s: re.sub(r"^/lib/", "/usr/lib/", s, 1))
df.original = df.original.apply(lambda s: re.sub(r"^/lib64/", "/usr/lib64/", s, 1))
df.changed = df.changed.apply(lambda s: re.sub(r"^(first|second)", "", s, 1))
df.changed = df.changed.apply(lambda s: re.sub(r"^/lib/", "/usr/lib/", s, 1))
df.changed = df.changed.apply(lambda s: re.sub(r"^/lib64/", "/usr/lib64/", s, 1))
df.to_csv('results.csv', index=False, header=False)


# # Symbols has two tests - we are using missing-previously-found-symbols
# df = df[df["analysis"] != "missing-previously-found-exports"]

# # Detect bad prediction values
# print(df["prediction"].unique())
# print((df["prediction"] == "Unknown").sum())
# df = df[df["prediction"] != "Unknown"]

# # Counts by analysis type
# counts=df.groupby(['predictor','analysis']).count()
# counts.drop(['a','b','changed','seconds','prediction'], axis=1, inplace=True)
# counts.rename(columns={"original":"count"}, inplace=True)
# counts

