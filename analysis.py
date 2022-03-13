#!/usr/bin/env python

import pandas
import argparse
import sys
import os
import json
import fnmatch
import shutil

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

here = os.getcwd()


def get_parser():
    parser = argparse.ArgumentParser(
        description="Splice Experiment Analyzer",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("results_dir", help="Directory with results.")
    parser.add_argument(
        "--outdir",
        help="Directory to save site data to (defaults to docs/).",
        default=os.path.join(os.getcwd(), "docs"),
    )
    return parser


# Helper Functions


def write_json(obj, filename, compact=False):
    with open(filename, "w") as fd:
        if compact:
            fd.write(json.dumps(obj))
        else:
            fd.write(json.dumps(obj, indent=4))


def read_json(filename):
    with open(filename, "r") as fd:
        content = json.loads(fd.read())
    return content


template = """---
title: Package %s Experiment %s results
categories: packages
tags: [package]
permalink: /results/%s/%s/
%s
maths: 1
toc: 1
---
"""


def get_experiments(rundir):
    experiments = {}
    for filename in recursive_find(rundir):
        experiments[filename] = read_json(filename)
    return experiments


def recursive_find(base, pattern="experiment.json"):
    for root, _, filenames in os.walk(base):
        for filename in fnmatch.filter(filenames, pattern):
            yield os.path.join(root, filename)


def summarize_experiments(experiments):
    """
    Given a dict of experiments, summarize results.
    """
    counts = {}

    # packages that were a install/splice success but not enough time for predictions
    success_no_predictions = set()

    # For the predictions we do have - let's make a table of

    # Total counts of predictions for each predictor
    predictions = {}
    for filename, exps in experiments.items():
        for exp in exps:

            # The label for the result
            if exp["result"] not in counts:
                counts[exp["result"]] = 0
            counts[exp["result"]] += 1

            # If we have success but no results, the install / splice was successful but predictions
            # were not run, likely a time issue
            if exp["success"] == True and not exp["predictions"]:
                success_no_predictions.add(exp["package"] + " splice " + exp["splice"])

            for name, prediction in exp["predictions"].items():
                if name not in predictions:
                    predictions[name] = 0
                predictions[name] += 1

    # These likely took so long to splice we didn't get to predictions
    counts["success-no-prediction"] = len(success_no_predictions)

    # This tells me we probably ran out of time (spack-test is usually run first)
    counts["predictions"] = predictions

    # NOTE the difference in 2.7K vs 3.4k jobs means some never got
    # to the part to save a result file
    return counts


def main():

    parser = get_parser()
    args, extra = parser.parse_known_args()

    # Make sure output directory exists
    outdir = os.path.abspath(args.outdir)
    if not os.path.exists(outdir):
        sys.exit("%s does not exist!" % outdir)

    # And the data directory
    datadir = os.path.join(outdir, "_data")
    if not os.path.exists(datadir):
        os.makedirs(datadir)

    # experiment name
    experiment = os.path.basename(args.results_dir)

    # logs must exist for full picture
    log_dir = os.path.abspath(os.path.join("log", experiment))
    if not os.path.exists(log_dir):
        sys.exit(
            "Log directory is required to get full picture: %s does not exist."
            % log_dir
        )

    # And the results (run) directory!
    if not args.results_dir or not os.path.exists(args.results_dir):
        sys.exit("%s does not exist!" % args.results_dir)

    results_dir = os.path.abspath(args.results_dir)
    experiments = get_experiments(results_dir)
    print("Found %s finished experimets." % len(experiments))

    # Save summary
    summary = summarize_experiments(experiments)
    summary["jobs-recorded"] = len(experiments)
    write_json(summary, os.path.join(datadir, "%s-summary.json" % experiment))
    del experiments

    # We will summarize on the level of each upper level package
    for pkg_dir in os.listdir(args.results_dir):
        pkg_dir = os.path.join(args.results_dir, pkg_dir)
        visualize_package(pkg_dir, experiment, outdir, log_dir)


def plot_clustermap(df, save_to=None):
    sns.set_theme(style="white")

    f, ax = plt.subplots(figsize=(30, 30))

    # Generate a custom diverging colormap
    cmap = sns.color_palette()
    # cmap = sns.diverging_palette(230, 20, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    p = sns.clustermap(
        df, cmap=cmap, center=0, linewidths=0.5, cbar_kws={"shrink": 0.5}
    )
    # used for heatmap
    # p.tick_params(labelsize=5)
    # p.set_xlabel("Splice", fontsize=12)
    # p.set_ylabel("Binary", fontsize=12)

    if save_to:
        plt.savefig(save_to)
    return plt


def plot_heatmap(df, save_to=None):
    sns.set_theme(style="white")

    f, ax = plt.subplots(figsize=(10, 12))

    # Generate a custom diverging colormap
    cmap = sns.color_palette()
    # cmap = sns.diverging_palette(230, 20, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    p = sns.heatmap(
        df, cmap=cmap, center=0, square=True, linewidths=0.5, cbar_kws={"shrink": 0.5}
    )
    # used for heatmap
    # p.tick_params(labelsize=5)
    # p.set_xlabel("Splice", fontsize=12)
    # p.set_ylabel("Binary", fontsize=12)

    if save_to:
        plt.savefig(save_to)
    return plt


def visualize_package(pkg_dir, experiment, outdir, log_dir):

    # There are TWO levels of informatoin
    # 1. The top level package / splice "was it successful or not (and if not why)
    # 2. The second level specific results for a splice "is this predicted to work (or not)"
    # For now I'm going to try and visualize the top, and then present the next levels in a table

    # Get experiment.json files for this package
    experiments = get_experiments(pkg_dir)

    # Package level summary
    summary = summarize_experiments(experiments)
    if not summary["predictions"]:
        del summary["predictions"]

    # We will create rows / cols for each splice
    rows = set()  # package
    cols = set()  # splices
    testers = set()  # predictors

    # Unique result types
    result_types = set()

    package = os.path.basename(pkg_dir)
    print("Analyzing %s" % package)

    # Results will be a table of results for each predictor
    results = {"failed": []}

    # Determine failures based on logs
    found_logs = set([x for x in os.listdir(log_dir) if x.startswith(package)])
    logs = {}

    # Keep list of files to copy for package
    tocopy = set()

    # Assemble experiments
    for filename, exps in experiments.items():

        # ID for the experiment group (associated with one log)
        exp_id = "-".join(filename.split(os.sep)[1:-1]) + "-experiment"

        # Look up logs to read and remove
        out_log = "%s.out" % exp_id
        err_log = "%s.err" % exp_id
        logs[exp_id] = {}

        # Allow each of out an error to not exist
        if os.path.exists(os.path.join(log_dir, out_log)):
            # We origially wrote logs here, but the context is too big!
            logs[exp_id]["out"] = os.path.join("logs", out_log)
            tocopy.add(out_log)
        else:
            logs[exp_id]["out"] = "Log is missing."

        if os.path.exists(os.path.join(log_dir, err_log)):
            logs[exp_id]["err"] = os.path.join("logs", err_log)
            tocopy.add(err_log)
        else:
            logs[exp_id]["err"] = "Log is missing."

        # Remove them from found logs
        for log in [out_log, err_log]:
            if log in found_logs:
                found_logs.remove(log)

        # 'run1/heffte/2.0.0/cmake/experiment.json'
        #      package version splice

        for exp in exps:

            # Top level results for the visualization go here
            cols.add(exp.get("splice"))
            rows.add(exp.get("package"))
            result_types.add(exp.get("result"))

            # If we don't have predictions, add to "failed" tester
            if exp["success"] == False and not exp["predictions"]:
                results["failed"].append(
                    {
                        "experiment": exp_id,
                        "splice": exp.get("splice"),
                        "package": exp.get("package"),
                        "result": exp.get("result"),
                    }
                )

            for tester, resultlist in exp["predictions"].items():
                if not resultlist:
                    continue
                testers.add(tester)
                if tester not in results:
                    results[tester] = []

                # We can't assume the testers have the exact same testing set (but they can)
                for res in resultlist:

                    # We add binaries/libs that we have predictions for
                    results[tester].append(
                        {
                            "binary": res.get("binary"),
                            "lib": res.get("lib"),
                            "prediction": res.get("prediction"),
                            "message": res.get("message"),
                            "return_code": res.get("return_code"),
                            "command": res.get("command"),
                            "splice": exp.get("splice"),
                            "package": exp.get("package"),
                            "result": exp.get("result"),
                            "experiment": exp_id,
                        }
                    )

    # These logs don't have associated results
    has_no_results = {}
    for log in found_logs:
        exp_id, log_type = log.rsplit(".", 1)
        if exp_id not in has_no_results:
            has_no_results[exp_id] = {}
        has_no_results[exp_id][log_type] = os.path.join("logs", log)

    summary["no-results-generated"] = len(has_no_results)
    summary["results-generated"] = len(logs)
    summary["total-runs"] = len(logs) + len(has_no_results)
    if testers:
        print("Found %s testers: %s" % (len(testers), " ".join(testers)))
    else:
        print("Found 0 testers")
    print(summary)

    # Create top level data frame
    # This data frame is the high level "did it work" df
    df = pandas.DataFrame(0, index=rows, columns=cols)

    # Assign each outcome a number
    outcomes = {result_type: i + 1 for i, result_type in enumerate(result_types)}

    # Populate outcomes
    for _, exps in experiments.items():
        for exp in exps:
            # Top level results for the visualization go here
            colname = exp.get("splice")
            rowname = exp.get("package")
            outcome = outcomes[exp.get("result")]
            df.loc[rowname, colname] = outcome

    # Save results to file under docs
    result_dir = os.path.join(outdir, "_results", experiment, package)
    result_logs_dir = os.path.join(result_dir, "logs")
    for dirname in [result_dir, result_logs_dir]:
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    for logfile in tocopy:
        shutil.copyfile(
            os.path.join(log_dir, logfile), os.path.join(result_logs_dir, logfile)
        )

    # Save the json to file
    write_json(results, os.path.join(result_dir, "results-list.json"), compact=True)
    df.to_json(os.path.join(result_dir, "results-table.json"))
    write_json(outcomes, os.path.join(result_dir, "outcomes.json"))
    if logs:
        write_json(logs, os.path.join(result_dir, "logs-existing.json"))
        logs = True
    if has_no_results:
        write_json(has_no_results, os.path.join(result_dir, "logs-missing.json"))
        has_no_results = True

    # Clean up
    del results

    # These get killed
    skips = ["py-libensemble", "heffte"]

    # Plot basics
    no_results = False
    if df.shape[1] == 0:
        print("Warning - empty data frame! No results to show for %s" % pkg_dir)
        no_results = True

    elif package in skips:
        print(
            "Skipping package %s, will kill computer memory to make matrix!" % package
        )

    elif df.shape[1] > 1 and df.shape[0] > 1:
        for ext in ["pdf", "png", "svg"]:
            save_to = os.path.join(result_dir, "%s-%s.%s" % (experiment, package, ext))
            fig = plot_clustermap(df, save_to)
    else:
        for ext in ["pdf", "png", "svg"]:
            save_to = os.path.join(result_dir, "%s-%s.%s" % (experiment, package, ext))
            fig = plot_heatmap(df, save_to)

    del df

    # These next dataframes are the "what do the predictions say" data frames
    # IMPORTANT this only represents what we can ACTUALLY PREDICT
    # failures to splice or spack choking cannot be here
    predicts = {}

    # Get rows and cols for each predictor
    for _, exps in experiments.items():
        for exp in exps:

            # We only have predictions on successful splice
            # to be clear, this experiment is not about predicting splices
            # we ASSUME correct splicing and then predict ABI compatibility
            for tester_name, preds in exp["predictions"].items():

                # here we are collapsing a set of predictions (across libs and binaries) into one set
                for pred in preds:
                    if tester_name not in predicts:
                        predicts[tester_name] = {}
                    if exp["package"] not in predicts[tester_name]:
                        predicts[tester_name][exp["package"]] = {}
                    if exp["splice"] not in predicts[tester_name][exp["package"]]:
                        predicts[tester_name][exp["package"]][exp["splice"]] = {
                            "total": 0,
                            "predict_work": 0,
                            "predict_fail": 0,
                        }
                    predicts[tester_name][exp["package"]][exp["splice"]]["total"] += 1
                    if pred["prediction"] == True:
                        predicts[tester_name][exp["package"]][exp["splice"]][
                            "predict_work"
                        ] += 1
                    else:
                        predicts[tester_name][exp["package"]][exp["splice"]][
                            "predict_fail"
                        ] += 1

    dfs = {}
    for tester_name, preds in predicts.items():
        rows = set()
        cols = set()
        for pkg, deps in preds.items():
            rows.add(pkg)
            [cols.add(x) for x in deps.keys()]
        dfs[tester_name] = pandas.DataFrame(0, index=list(rows), columns=list(cols))
        for pkg, deps in preds.items():
            for dep, counts in deps.items():
                dfs[tester_name].loc[pkg, dep] = (
                    counts["predict_work"] / counts["total"]
                )

    # Clean up
    del predicts

    # Save each matrix to file
    no_results = False
    for tester_name, df in dfs.items():
        if df.shape[1] == 0:
            print("Warning - empty data frame! No results to show for %s" % pkg_dir)
            no_results = True

        elif df.shape[1] > 1 and df.shape[0] > 1:
            for ext in ["pdf", "png", "svg"]:
                save_to = os.path.join(
                    result_dir, "%s-%s-%s.%s" % (tester_name, experiment, package, ext)
                )
                fig = plot_clustermap(df, save_to)
        else:
            for ext in ["pdf", "png", "svg"]:
                save_to = os.path.join(
                    result_dir, "%s-%s-%s.%s" % (tester_name, experiment, package, ext)
                )
                fig = plot_heatmap(df, save_to)
        del df

    # Save the filenames for images
    listing = ""
    if not no_results:
        if package not in skips:
            for ext in ["pdf", "png", "svg"]:
                listing += "%s: %s-%s.%s\n" % (ext, experiment, package, ext)
            for tester_name, _ in dfs.items():
                for ext in ["pdf", "png", "svg"]:
                    listing += "%s-%s: %s-%s-%s.%s\n" % (
                        tester_name,
                        ext,
                        tester_name,
                        experiment,
                        package,
                        ext,
                    )

        # And the entry for the results
        listing += "results: results-list.json\n"
        listing += "outcomes: %s\n" % outcomes
        listing += "summary: %s\n" % summary
        if logs:
            listing += "logs_existing: logs-existing.json\n"
        if has_no_results:
            listing += "logs_missing: logs-missing.json"

        # Generate a markdown for each
        content = template % (package, experiment, experiment, package, listing)

        md = os.path.join(result_dir, "index.md")
        with open(md, "w") as fd:
            fd.write(content)


if __name__ == "__main__":
    main()
