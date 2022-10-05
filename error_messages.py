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

def disagreement_by_analysis(a1, a2, filename_changed):
  changed="original<>changed" if filename_changed else "original=changed"
  
  query = f"""
    select
      p1.a,
      p1.b,
      p1.original
    from
      (select a,b,original,prediction from three_predictors where {changed} and analysis='{a1}') as p1
      join
      (select a,b,original,prediction from three_predictors where {changed} and analysis='{a2}') as p2
      on
        p1.a = p2.a
        and p1.b = p2.b
        and p1.original = p2.original
    where
      p1.prediction <> p2.prediction
    """
  cur.execute(query)
  return cur.fetchall()

def predictor_by_analysis(analysis):
  if analysis == 'abidiff':
    return 'libabigail'
  if analysis == 'abi-compliance-tester':
    return 'abi-laboratory'
  return 'symbols'

analyses = (
  ('abidiff','abi-compliance-tester'),
  ('abidiff','missing-previously-found-symbols'),
  ('abidiff','missing-previously-found-exports'),
  ('abi-compliance-tester','missing-previously-found-symbols'),
  ('abi-compliance-tester','missing-previously-found-exports'),
  ('missing-previously-found-symbols','missing-previously-found-exports')
)

for analysis in analyses:
  for fnc in (True, False):
    with open("three_predictors.{0}.{1}.{2}.messages.disagreement".format("changed" if fnc else "unchanged", analysis[0], analysis[1]), "w") as fdout:
      for l in disagreement_by_analysis(analysis[0], analysis[1], fnc):
        a,b,libpath = l
        dir, libname = os.path.split(libpath)
        prefix = libname.split(".")[0]
        filename = f"artifacts/results/extracted/fedora/{dir}/{prefix}-{a}-{b}.json"
       
        with open(filename, "r") as fd:
          res = json.loads(fd.read())[0]
  
        print(f"FILE--{filename}", file=fdout)
        for p in [predictor_by_analysis(a) for a in analysis]:
          for r in res["predictions"][p]:
            if "message" in r and r["message"]:
              if p == 'abi-laboratory' and str(r["prediction"]) == "True":
                continue
              msg = r["message"]
              if isinstance(msg, list):
                msg = ' '.join(msg)
              print("{0},{1}--{2}".format(r["command"] if p=="symbols" else p, r["prediction"], msg.replace("\n", " ")), file=fdout)


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
