import sys
import os
sys.path.insert(0, os.getcwd())
from helpers import recursive_find, create_fedora_results_table

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
