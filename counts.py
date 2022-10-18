import sqlite3
con = sqlite3.connect('results.sqlite3')
cur = con.cursor()

def disagreement(table, pred1_name, pred1_state, pred2_name, pred2_state, filename_changed):
    query = f"""
    SELECT
        count(1) as cnt
    FROM
        {table} as pr
        JOIN  (
        SELECT DISTINCT a,b,original FROM {table} WHERE analysis=? and prediction=?
        ) AS syms ON
            pr.a = syms.a
            and pr.b = syms.b
            and pr.original = syms.original
    WHERE
        analysis=?
        and pr.prediction=?
    """

    if(filename_changed):
        query += " and pr.original<>pr.changed"
    else:
        query += " and pr.original=pr.changed"

    cur.execute(query, (pred1_name, pred1_state, pred2_name, pred2_state))
    return cur.fetchone()

def run(table, predictors):
    for fnc in (True, False):
        print("filename {0:s}changed".format("" if fnc else "un"), "\n", "-"*20)
        for p1 in predictors:
            print(p1)
            padding = '  '
            for p2 in predictors:
                print(padding, p2)
                print(padding, *disagreement(table, p1, 'True', p2, 'True', filename_changed=fnc),',',end='')
                print(padding, *disagreement(table, p1, 'True', p2, 'False', filename_changed=fnc),',',end='')
                print(padding, *disagreement(table, p1, 'False', p2, 'True', filename_changed=fnc),',',end='')
                print(padding, *disagreement(table, p1, 'False', p2, 'False', filename_changed=fnc))
        print("\n")

predictors=('missing-previously-found-symbols', 'abidiff')
run('two_predictors', predictors)

predictors=('missing-previously-found-symbols', 'abidiff', 'abi-compliance-tester')
run('three_predictors', predictors)

print("Average fraction of libraries")
print('-'*70)
# How many files are lost when we run three predictors due to crashes in abilab
cur.execute("""
select
  (twop.cnt-threep.cnt)/((twop.cnt+threep.cnt)/2.0) * 100.0 as pdiff
from
  (select a,b,count(distinct original) as cnt from two_predictors group by a,b) as twop
  join (select a,b,count(distinct original) as cnt from three_predictors group by a,b) as threep on
    twop.a= threep.a
    and twop.b = threep.b
""")
pdiff=[]
print("missing in the three-predictor case:")
for r in cur.fetchall():
  pdiff.append(r[0])
print("  avg: {0:.2f}%, min: {1:.2f}%, max: {2:.2f}%".format(sum(pdiff)/len(pdiff), min(pdiff), max(pdiff)))


# Average fraction of libraries by predictor and filename cases
# Only show for changed case- changed cases are complementary
def frac_by_category(table):
  cur.execute(f"""
    select
      c1.cnt/cast(c2.cnt as float)*100.0 as frac
    from
      (select a,b,count(distinct original) as cnt from {table} where original<>changed group by a,b) as c1
      join (select a,b,count(distinct original) as cnt from {table} group by a,b) as c2 on
        c1.a=c2.a
        and c1.b=c2.b
    """)
  return cur.fetchall()

print("\nBy predictor count, filename status")
for t in ('two_predictors','three_predictors'):
  frac=[]
  for r in frac_by_category(t):
    frac.append(r[0])
  print("  {0}, changed: avg: {1:.2f}%, min: {2:.2f}%, max: {3:.2f}%".format(t, sum(frac)/len(frac), min(frac), max(frac)))

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

print("\nAt least one break detected:")
for t in ('two_predictors','three_predictors'):
  for fnc in (True, False):
    frac=[]
    for r in frac_breakages(t,fnc):
      frac.append(r[0])
    print("  {0}, {1:s}changed: avg: {2:.2f}%, min: {3:.2f}%, max: {4:.2f}%".format(
      t, "" if fnc else "un", sum(frac)/len(frac), min(frac), max(frac)))
