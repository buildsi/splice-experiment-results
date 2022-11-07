#!/usr/bin/env python3

import sqlite3

con = sqlite3.connect("results.sqlite3")
cur = con.cursor()

def counts(table, fnc):
  filter = "original<>changed" if fnc else "original=changed"
  cur.execute(
    f"""
      select a,b, count(distinct original) from {table} where {filter} group by a,b
    """
  )
  return cur.fetchall()


print("Number of libraries by predictor and filename cases")
print("-" * 70)
for t in ("two_predictors", "three_predictors"):
  for fnc in (True, False):
    print("{0:s} {1:s}changed".format(t, "" if fnc else "un"))
    for r in counts(t,fnc):
      print("  ", r)
