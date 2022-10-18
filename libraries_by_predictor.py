import sqlite3
con = sqlite3.connect('results.sqlite3')
cur = con.cursor()

# Average fraction of libraries by predictor and filename cases
# Only show for changed case- unchanged cases are complementary
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

print("Average fraction of libraries by predictor and filename cases")
print('-'*70)
for t in ('two_predictors','three_predictors'):
  frac=[]
  for r in frac_by_category(t):
    frac.append(r[0])
  print("  {0}, changed: avg: {1:.2f}%, min: {2:.2f}%, max: {3:.2f}%".format(t, sum(frac)/len(frac), min(frac), max(frac)))
