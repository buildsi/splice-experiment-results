import sqlite3
con = sqlite3.connect('results.sqlite3')
cur = con.cursor()

# At least one predictor detects a breakage
def frac_breakages(table, fnc):
  filter="original<>changed" if fnc else "original=changed"
  cur.execute(f"""
    select
      sum(case prediction when 'False' then 1 else 0 end) / cast(count(1) as float) * 100.0 as frac
    from
      {table}
    where
      {filter}
    group by
      a,b
    having
      sum(case prediction when 'False' then 1 else 0 end) > 0
    """)
  return cur.fetchall()

print("At least one predictor detects a breakage:")
print('-'*70)
for t in ('two_predictors','three_predictors'):
  for fnc in (True, False):
    frac=[]
    for r in frac_breakages(t,fnc):
      frac.append(r[0])
    print("  {0}, {1:s}changed: avg: {2:.2f}%, min: {3:.2f}%, max: {4:.2f}%".format(
      t, "" if fnc else "un", sum(frac)/len(frac), min(frac), max(frac)))
