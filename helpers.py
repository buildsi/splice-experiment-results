import os
import pandas
from glob import glob
import fnmatch
import json


def recursive_find(base, pattern="*experiment.json"):
    """recursive find will yield python files in all directory levels
       below a base path.

       Arguments:
         - base (str) : the base directory to search
         - pattern: a pattern to match, defaults to *.py
    """
    for root, _, filenames in os.walk(base):
        for filename in fnmatch.filter(filenames, pattern):
            yield os.path.join(root, filename)
            
def read_json(filename):
    with open(filename, 'r') as fd:
        content = json.loads(fd.read())
    return content
    
def create_results_table(experiments):    
    """
    Given experiments data files, iterate through and create a results table that includes splice details
    """
    df = pandas.DataFrame(columns=["original", "changed", "analysis", "compiler", "seconds", "predictor", "prediction"])

    def add_prediction_row(original, changed, compiler, res, p, predictor):               
        """
        Given a result, add a row to the data frame.
        """
        # Different predictors use different data
        prediction = p.get('prediction', False)
        seconds = p.get('seconds') or "unknown"
    
        # symbols has two diff cases
        analysis = "abi-compliance-tester"
        if predictor == "symbols":
            analysis = p['command']
        elif predictor == "libabigail":
            analysis = "abidiff"
        elif predictor == 'smeagle':
            analysis = "smeagle-stability-test"
        
        df.loc[len(df.index),:] = [original, changed, analysis, compiler, seconds, predictor, prediction]    
    
    # Of the splice successes, now look into results
    for e in experiments:
        compiler = e.split('/')[-2]
        data = read_json(e)
        for res in data:
            
            # Split on right repo name to get relative path
            original = res['original'][0].rsplit('splice-experiment-runs')[-1].strip('/')
            changed = res['spliced'][0].rsplit('splice-experiment-runs')[-1].strip('/')

            for predictor, listing in res['predictions'].items():
                for p in listing:
                    add_prediction_row(original, changed, compiler, res, p, predictor)           
    return df

    
def create_sizes_table(experiments):
    """
    Keep track of all binary sizes
    """
    sizes = pandas.DataFrame(columns=["name", "size_bytes"])
    for e in experiments:
        data = read_json(e)
        for res in data:
            if res['result'] != "splice-success":
                continue
            for libname, size in res['stats']['sizes_bytes'].items():
                sizes.loc[len(sizes.index),:] = [libname, size]
            
    return sizes

