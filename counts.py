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



