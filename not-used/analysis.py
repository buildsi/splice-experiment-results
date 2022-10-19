#!/usr/bin/env python

import argparse
import fnmatch
import json
import os
import shutil
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas
import seaborn as sns
from matplotlib.patches import Patch

here = os.getcwd()
sys.path.insert(0, here)


from helpers import create_results_table

sns.set_theme(style="white")
sns.set(font_scale=1.4)


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
    parser.add_argument(
        "--experiment-name",
        dest="experiment",
        help="Name for experiment",
        default="spliced-experiment",
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
title: Experiment %s Results
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


def summarize_experiments(df):
    """
    Given a dict of experiments, summarize results (confusion matrices)
    """
    summary = {}

    # Truth tables by predictor, first across all compilers
    for predictor in df["predictor"].unique():
        df_tmp = df[df["predictor"] == predictor]
        confusion = pandas.crosstab(
            df_tmp["prediction"],
            df_tmp["truth"],
            rownames=["prediction"],
            colnames=[predictor],
        )
        summary[predictor] = confusion.to_dict()
    return summary


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
    experiment = args.experiment

    # And the results (run) directory!
    if not args.results_dir or not os.path.exists(args.results_dir):
        sys.exit("%s does not exist!" % args.results_dir)

    results_dir = os.path.abspath(args.results_dir)

    # Data frame is used for confusion matrices, etc. (include filename)
    df = create_results_table(recursive_find(results_dir), True)
    df["label"] = df["predictor"] + " " + df["analysis"]

    # Experiments have full metadata
    experiments = get_experiments(results_dir)
    print("Found %s finished experiments." % len(experiments))

    # All breaks are False (meaning shouldn't work)
    df["truth"] = False

    # Save summary of confusion matrices
    summary = summarize_experiments(df)
    write_json(summary, os.path.join(datadir, "%s-summary.json" % experiment))
    write_json(
        df.to_dict(orient="records"), os.path.join(datadir, "%s-df.json" % experiment)
    )

    # We will summarize on the level of each break
    for breakage in df["changed"].unique():
        df_tmp = df[df["changed"] == breakage]
        visualize_package(breakage, df_tmp, experiment, outdir, experiments)


def plot_heatmap(df, save_to=None):
    f, ax = plt.subplots(figsize=(12, 12))

    # Generate a custom diverging colormap
    # cmap = sns.diverging_palette(230, 3, as_cmap=True)
    cmap = sns.mpl_palette("Set2", 2)

    # Draw the heatmap with the mask and correct aspect ratio
    p = sns.heatmap(df.astype(int), linewidths=0.5, cbar=False, cmap=cmap)
    # used for heatmap
    # p.tick_params(labelsize=5)
    # plt.set_xlabel("Splice", fontsize=12)
    # lt.set_ylabel("Binary", fontsize=12)
    legend_handles = [
        Patch(color=cmap[1], label="Predicted to Work (wrong)"),
        Patch(color=cmap[0], label="Predicted to Fail (correct)"),
    ]
    plt.legend(
        handles=legend_handles,
        ncol=2,
        bbox_to_anchor=[0.5, 1.02],
        loc="lower center",
        fontsize=8,
        handlelength=0.8,
    )
    plt.tight_layout()
    if save_to:
        plt.savefig(save_to)
        plt.close()


def visualize_package(breakage, subset, experiment, outdir, experiments):

    # Create data frame of breaks (rows) by compilers (column) and prediction
    compilers = list(subset["compiler"].unique())
    labels = list(subset["label"].unique())

    df = pandas.DataFrame(columns=compilers, index=labels)
    summary = summarize_experiments(subset)

    # Populate outcomes
    for compiler in compilers:
        for label in labels:
            row = subset[(subset["compiler"] == compiler) & (subset["label"] == label)]
            df.loc[label, compiler] = int(row.prediction.values[0])

    # Save results to file under docs
    break_dir = os.path.dirname(breakage)
    result_dir = os.path.join(outdir, "_results", experiment, break_dir)

    # Create organized set of results
    files = list(subset.file)
    results = {}
    for filename, result in experiments.items():
        if filename in files:
            compiler = os.path.basename(os.path.dirname(filename))
            if len(result) > 1:
                raise ValueError("Found result %s with length > 1" % filename)
            results[compiler] = result[0]

    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    # Save the json to file
    write_json(results, os.path.join(result_dir, "results-list.json"), compact=True)
    df.to_json(os.path.join(result_dir, "results-table.json"))
    subset.to_json(os.path.join(result_dir, "df-subset.json"))

    for ext in ["pdf", "png", "svg"]:
        save_to = os.path.join(result_dir, "%s-table.%s" % (experiment, ext))
        fig = plot_heatmap(df, save_to)

    # Save the filenames for images
    listing = ""
    for ext in ["pdf", "png", "svg"]:
        listing += "%s: %s-table.%s\n" % (ext, experiment, ext)

    # And the entry for the results
    listing += "results: results-list.json\n"
    listing += "table: results-table.json\n"
    listing += "data: df-subset.json\n"
    listing += "summary: %s\n" % summary

    # Generate a markdown for each
    content = template % (break_dir, experiment, break_dir, listing)
    md = os.path.join(result_dir, "index.md")
    with open(md, "w") as fd:
        fd.write(content)


if __name__ == "__main__":
    main()
