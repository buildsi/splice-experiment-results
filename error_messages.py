import os
import json
import sqlite3

con = sqlite3.connect('results.sqlite3')
cur = con.cursor()

def any_disagreements(table, filename_changed, max_match):
  changed="original<>changed" if filename_changed else "original=changed"
  
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
      sum(case prediction when "True" then 1 else 0 end) not in(0,{max_match})
    """

  cur.execute(query)
  return cur.fetchall()

predictors = {
  'two_predictors': ("libabigail", "symbols"),
  'three_predictors': ("libabigail", "symbols", "abi-laboratory")
}
for t,m in (('two_predictors',3), ('three_predictors',4)):
    for fnc in (True, False):
      with open("{0}.{1}.messages".format(t, "changed" if fnc else "unchanged"), "w") as fdout:
        for l in any_disagreements(t, fnc, max_match=m):
          a,b,libpath = l
          dir, libname = os.path.split(libpath)
          prefix = libname.split(".")[0]
          filename = f"artifacts/results/extracted/fedora/{dir}/{prefix}-{a}-{b}.json"

          with open(filename, "r") as fd:
            res = json.loads(fd.read())[0]

          print(f"FILE--{filename}", file=fdout)
          for p in predictors[t]:
            for r in res["predictions"][p]:
              if "message" in r and r["message"]:
                if p == 'abi-laboratory' and str(r["prediction"]) == "True":
                  continue
                msg = r["message"]
                if isinstance(msg, list):
                  msg = ' '.join(msg)
                print("{0},{1}--{2}".format(r["command"] if p=="symbols" else p, r["prediction"], msg.replace("\n", " ")), file=fdout)
