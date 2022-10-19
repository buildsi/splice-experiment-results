#!/usr/bin/env python3

import json
import os
import sqlite3

con = sqlite3.connect("results.sqlite3")
cur = con.cursor()


def any_disagreements(table, filename_changed):
    changed = "original<>changed" if filename_changed else "original=changed"

    # A prediction of 1 is False (error code) and 0 is True (will work)
    query = f"""
    select
      a,b,original
    from
      {table}
    where
      {changed}
    group by
      a,b,original
    having
      sum(case prediction when 1 then 1 else 0 end) > 0
    """

    cur.execute(query)
    return cur.fetchall()


predictors = {
    "two_predictors": ("libabigail", "symbols"),
    "three_predictors": ("libabigail", "symbols", "abi-laboratory"),
}


def main():
    for t in ("two_predictors", "three_predictors"):
        for fnc in (True, False):
            output_file = "{0}.{1}.messages".format(
                t, "changed" if fnc else "unchanged"
            )
            print(f"⭐️ Writing {output_file}")
            with open(output_file, "w") as fdout:
                for l in any_disagreements(t, fnc):
                    a, b, libpath = l
                    dir, libname = os.path.split(libpath)
                    prefix = libname.split(".")[0]
                    filename = f"artifacts/results/extracted/fedora/{dir}/{prefix}-{a}-{b}.json"

                    with open(filename, "r") as fd:
                        res = json.loads(fd.read())[0]

                    print(f"FILE--{filename}", file=fdout)
                    for p in predictors[t]:
                        for r in res["predictions"][p]:
                            if "message" in r:
                                # Some predictors have output even when they return True; skip it
                                if str(r["prediction"]) == "True":
                                    continue
                                msg = r["message"]
                                if isinstance(msg, list):
                                    msg = " ".join(msg)
                                print(
                                    "{0},{1}--{2}".format(
                                        r["command"] if p == "symbols" else p,
                                        r["prediction"],
                                        msg.replace("\n", " "),
                                    ),
                                    file=fdout,
                                )


if __name__ == "__main__":
    main()
