#!/usr/bin/env python3

import sqlite3

con = sqlite3.connect("results.sqlite3")
cur = con.cursor()

print("Average fraction of libraries missing in the three-predictor case:")
print("-" * 70)

# How many files are lost when we run three predictors due to crashes in abilab
cur.execute(
    """
select
  (twop.cnt-threep.cnt)/((twop.cnt+threep.cnt)/2.0) * 100.0 as pdiff
from
  (select a,b,count(distinct original) as cnt from two_predictors group by a,b) as twop
  join (select a,b,count(distinct original) as cnt from three_predictors group by a,b) as threep on
    twop.a= threep.a
    and twop.b = threep.b
"""
)
pdiff = []
for r in cur.fetchall():
    pdiff.append(r[0])
print(
    "  avg: {0:.2f}%, min: {1:.2f}%, max: {2:.2f}%".format(
        sum(pdiff) / len(pdiff), min(pdiff), max(pdiff)
    )
)
