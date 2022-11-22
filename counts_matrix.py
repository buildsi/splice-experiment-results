#!/usr/bin/env python3

import sqlite3

con = sqlite3.connect("results.sqlite3")
cur = con.cursor()


def disagreement(
    table, pred1_name, pred1_state, pred2_name, pred2_state, filename_changed
):
    changed = "original<>changed" if filename_changed else "original=changed"
    query = f"""
    select
      count(1)
    from
    (
      select
        distinct a,b,original
      from
        {table}
      where
        analysis = '{pred1_name}'
        and prediction = '{pred1_state}'
        and {changed}
    ) as pred1 join (
      select
        distinct a,b,original
      from
        {table}
      where
        analysis = '{pred2_name}'
        and prediction = '{pred2_state}'
        and {changed}
    ) as pred2 on
      pred1.a = pred2.a
      and pred1.b = pred2.b
      and pred1.original = pred2.original
    """

    cur.execute(query)
    return cur.fetchone()


def run(table, predictors):
    for fnc in (True, False):
        print("filename {0:s}changed".format("" if fnc else "un"), "\n", "-" * 20)
        for p1 in predictors:
            print(p1)
            padding = "  "
            for p2 in predictors:
                print(padding, p2)
                print(
                    padding,
                    *disagreement(table, p1, 1, p2, 1, filename_changed=fnc),
                    ",",
                    end="",
                )
                print(
                    padding,
                    *disagreement(table, p1, 1, p2, 0, filename_changed=fnc),
                    ",",
                    end="",
                )
                print(
                    padding,
                    *disagreement(table, p1, 0, p2, 1, filename_changed=fnc),
                    ",",
                    end="",
                )
                print(
                    padding,
                    *disagreement(table, p1, 0, p2, 0, filename_changed=fnc),
                )
        print("\n")


predictors = ("missing-previously-found-exports", "abidiff")
run("two_predictors", predictors)

predictors = ("missing-previously-found-exports", "abidiff", "abi-compliance-tester")
run("three_predictors", predictors)
