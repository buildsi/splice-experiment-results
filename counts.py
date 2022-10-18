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
