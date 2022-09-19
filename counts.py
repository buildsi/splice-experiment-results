import sqlite3
from Xlib.error import BadFont
con = sqlite3.connect('results.sqlite3')
cur = con.cursor()

def disagreement(table, pred1_name, pred1_state, pred2_name, pred2_state):
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
    cur.execute(query, (pred1_name, pred1_state, pred2_name, pred2_state))
    return cur.fetchone()

predictors=('missing-previously-found-exports', 'missing-previously-found-symbols', 'abidiff')
for p1 in predictors:
    for p2 in predictors:
        print(*disagreement('two_predictors', p1, 'True', p2, 'True'),',',end='')
        print(*disagreement('two_predictors', p1, 'True', p2, 'False'),',',end='')
        print(*disagreement('two_predictors', p1, 'False', p2, 'True'),',',end='')
        print(*disagreement('two_predictors', p1, 'False', p2, 'False'))
    print("\n")

predictors=('missing-previously-found-exports', 'missing-previously-found-symbols', 'abidiff', 'abi-compliance-tester')
for p1 in predictors:
    for p2 in predictors:
        print(*disagreement('three_predictors', p1, 'True', p2, 'True'),',',end='')
        print(*disagreement('three_predictors', p1, 'True', p2, 'False'),',',end='')
        print(*disagreement('three_predictors', p1, 'False', p2, 'True'),',',end='')
        print(*disagreement('three_predictors', p1, 'False', p2, 'False'))
    print("\n")


def get_prefix(lib):
    import os
    return os.path.basename(lib).split(".")[0]