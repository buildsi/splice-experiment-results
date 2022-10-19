#!/usr/bin/env python3

import sqlite3

con = sqlite3.connect("results.sqlite3")
cur = con.cursor()


def agreement(table, filename_changed, max_match):
    changed = "original<>changed" if filename_changed else "original=changed"

    query = f"""
			select
				count(1) / cast((select count(distinct original) from {table} where {changed}) as float)
			from (
				select
					1
				from
					{table}
				where
				  {changed}
				group by
					original
				having
					count(case prediction when 1 then 1 else 0 end) in(0,{max_match})
			)
			"""

    cur.execute(query)
    return cur.fetchone()


for t, m in (("two_predictors", 3), ("three_predictors", 4)):
    print(f"Table: {t}\n", "-" * 20)
    for fnc in (True, False):
        print(
            "  ",
            "filename {0:s}changed".format("" if fnc else "un"),
            ":",
            100.0 * agreement(t, fnc, max_match=m)[0],
        )
    print()
