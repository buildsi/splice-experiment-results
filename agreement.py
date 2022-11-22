#!/usr/bin/env python3

import sqlite3

con = sqlite3.connect("results.sqlite3")
cur = con.cursor()


def agreement(table, filename_changed, max_match):
    changed = "original<>changed" if filename_changed else "original=changed"

    query = f"""
      select
        agree.cnt / cast(total.cnt as float) * 100.0
      from
      (
        select
          a, b, count(1) as cnt
        from
        (
          select
            a, b, original
          from
            {table}
          where
            {changed}
          group by
            a, b, original
          having
            sum(prediction) in(0, {max_match})
        )
        group by a, b
      ) as agree
      join (
        select
          a,b,count(distinct original) as cnt
        from
          {table}
        where
          {changed}
        group by a,b
      ) as total on
        agree.a = total.a
        and agree.b = total.b
		"""

    cur.execute(query)
    return cur.fetchall()


print("Fraction of libraries where all predictors agree:")
print("-" * 70)
for t, m in (("two_predictors", 2), ("three_predictors", 3)):
    print(f" {t}\n", "-" * 20)
    for fnc in (True, False):
        frac = []
        for r in agreement(t, fnc, max_match=m):
            frac.append(r[0])
        print(
            "  {0:s}changed: avg: {1:.2f}%, min: {2:.2f}%, max: {3:.2f}%".format(
                "" if fnc else "un", sum(frac) / len(frac), min(frac), max(frac)
            )
        )
    print()
