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
    with open(filename, "r") as fd:
        content = json.loads(fd.read())
    return content


def create_results_table(experiments, filename=False):
    """
    Given experiments data files, iterate through and create a results table that includes splice details
    """
    columns = [
        "original",
        "changed",
        "analysis",
        "compiler",
        "seconds",
        "predictor",
        "prediction",
    ]
    if filename:
        columns.append("file")
    df = pandas.DataFrame(columns=columns)

    def add_prediction_row(original, changed, compiler, res, p, predictor, e):
        """
        Given a result, add a row to the data frame.
        """
        # Different predictors use different data
        prediction = p.get("prediction", False)
        seconds = p.get("seconds") or "unknown"

        # symbols has two diff cases
        analysis = "abi-compliance-tester"
        if predictor == "symbols":
            analysis = p["command"]
        elif predictor == "libabigail":
            analysis = "abidiff"

        # Smeagle results not included in this paper
        elif predictor == "smeagle":
            return
        row = [
            original,
            changed,
            analysis,
            compiler,
            seconds,
            predictor,
            prediction,
        ]
        if filename:
            row.append(e)
        df.loc[len(df.index), :] = row

    # Of the splice successes, now look into results
    for e in experiments:
        compiler = e.split("/")[-2]
        data = read_json(e)
        for res in data:

            # Split on right repo name to get relative path
            original = (
                res["original"][0].rsplit("splice-experiment-runs")[-1].strip("/")
            )
            changed = res["spliced"][0].rsplit("splice-experiment-runs")[-1].strip("/")

            for predictor, listing in res["predictions"].items():
                for p in listing:
                    add_prediction_row(
                        original, changed, compiler, res, p, predictor, e
                    )
    return df


def create_fedora_results_table(experiments, filename=False):
    """
    Given experiments data files, iterate through and create a results table that includes splice details
    """
    columns = [
        "a",
        "b",
        "original",
        "changed",
        "analysis",
        "seconds",
        "predictor",
        "prediction",
    ]
    if filename:
        columns.append("file")
    df = pandas.DataFrame(columns=columns)

    def add_prediction_row(before, after, original, changed, p, predictor, e):
        """
        Given a result, add a row to the data frame.
        """
        # Different predictors use different data
        prediction = p.get("prediction", False)
        seconds = p.get("seconds") or p.get('time') or "unknown"

        # symbols has two diff cases
        analysis = "abi-compliance-tester"
        if predictor == "symbols":
            analysis = p['command']
        elif predictor == "libabigail":
            analysis = "abidiff"

        row = [
            before,
            after,
            original,
            changed,
            analysis,
            seconds,
            predictor,
            prediction,
        ]
        if filename:
            row.append(e)
        df.loc[len(df.index), :] = row

    # Of the splice successes, now look into results
    for e in experiments:
        basename = os.path.basename(e)
        libname, comparison = basename.split('-', 1)
        comparison = comparison.replace('.json', '')        
        comparison = [(f"fedora{x}").strip('-') for x in comparison.rsplit('fedora') if x]
        before = comparison[-2]
        after = comparison[-1]
        data = read_json(e)

        # Symbols libs have one result per file - flattened
        if "fedora/symbols" in e:
            data = [data]

        for res in data:

            # If we don't have predictions, it's a full (non symbols) result
            if "predictions" not in res:                
                continue
            else:
                # Split on right repo name to get relative path
                original = (
                    res["original"][0].rsplit("splice-experiment-runs")[-1].strip("/")
                )
                changed = res["spliced"][0].rsplit("splice-experiment-runs")[-1].strip("/")
                for predictor, listing in res["predictions"].items():
                    for p in listing:
                        # ABI lab has several terminated results for "stack smashing"
                        if "message" in p and isinstance(p['message'], str) and "***: terminated" in p['message'].lower():
                            p['prediction'] = "Terminated"
                        add_prediction_row(before, after, original, changed, p, predictor, e)
    return df

def create_sizes_table(experiments):
    """
    Keep track of all binary sizes

    (this is currently not used)
    """
    sizes = pandas.DataFrame(columns=["name", "size_bytes"])
    for e in experiments:
        data = read_json(e)
        for res in data:
            if res["result"] != "splice-success":
                continue
            for libname, size in res["stats"]["sizes_bytes"].items():
                sizes.loc[len(sizes.index), :] = [libname, size]

    return sizes
