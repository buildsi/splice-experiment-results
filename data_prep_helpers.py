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
    df = pandas.DataFrame(columns=["package", "dependency", "original_lib", "spliced_lib", "binary", "prediction", "predictor", "seconds", "command"])

    def add_prediction_row(res, p, predictor):               
        """
        Given a result, add a row to the data frame.
        """
        # Different predictors use different data
        prediction = p.get('prediction', False)
        original_lib = p.get('original_lib') or "not used"
        spliced_lib = p.get('spliced_lib') or "not used"
        binary = p.get('binary') or "not used"
        command = p.get('command') or "unknown"
        seconds = p.get('seconds') or "unknown"
        df.loc[len(df.index),:] = [res['package'], res['splice'], original_lib, spliced_lib, binary, prediction, predictor, seconds, command]    
    
    # Of the splice successes, now look into results
    for e in experiments:
        data = read_json(e)
        for res in data:
            if res['result'] != "splice-success":
                continue
            for predictor, listing in res['predictions'].items():
                # Can't compare smeagle to the duo/trio case
                if predictor == "smeagle":
                    for p in listing:
                        if "prediction" in p:
                            add_prediction_row(res, p, "smeagle")
           
                # Spack test has results under original/spliced
                elif predictor == "symbols":
                    for p in listing:
                        if "binary-checks-symbol-provisioner-change" in p.get('command', ''):
                            add_prediction_row(res, p, "binary-checks-symbol-provisioner-change")
                        elif "missing-previously-found-symbols" in p.get('command', ''):
                            add_prediction_row(res, p, "missing-previously-found-symbols")
                        elif "binary-checks-loader-missing-symbols-for-original" in p.get('command', ''):
                            add_prediction_row(res, p, "binary-checks-loader-missing-symbols-for-original")
                        else:
                            add_prediction_row(res, p, predictor)

                elif predictor == "spack-test":
                    add_prediction_row(res, listing['original'], 'spack-test-original')
                    add_prediction_row(res, listing['spliced'], 'spack-test-spliced')
                else:
                    for p in listing:
                        if "abicompat" in p.get('command', ''):
                            add_prediction_row(res, p, "libabigail-abicompat")
                        elif "abidiff" in p.get('command', ''):
                            add_prediction_row(res, p, "libabigail-abidiff")
                        else:
                            add_prediction_row(res, p, predictor)
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
