#!/usr/bin/env python

import pandas
import argparse
import sys
import os
import json
import fnmatch
import shutil
import string

import numpy as np
import seaborn as sns
import secrets
import matplotlib.pyplot as plt

here = os.getcwd()


def get_parser():
    parser = argparse.ArgumentParser(
        description="Splice Experiment Graph Dumper",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("results_dir", help="Directory with results.")
    parser.add_argument("--outdir", help="path to output directory")
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


def get_experiments(rundir):
    experiments = {}
    for filename in recursive_find(rundir):
        experiments[filename] = read_json(filename)
    return experiments


def recursive_find(base, pattern="experiment.json"):
    for root, _, filenames in os.walk(base):
        for filename in fnmatch.filter(filenames, pattern):
            yield os.path.join(root, filename)


def main():

    parser = get_parser()
    args, extra = parser.parse_known_args()

    # And the results (run) directory!
    for dirname in [args.results_dir, args.outdir]:
        if not dirname or not os.path.exists(dirname):
            sys.exit("%s does not exist!" % dirname)

    # experiment name
    experiments = get_experiments(args.results_dir)

    # First derive success nodes and edges
    outcomes = get_outcomes(experiments)
    write_json(outcomes, os.path.join(args.outdir, "libabigail-outcomes.json"))

    write_cypher(outcomes, args.outdir)


def write_cypher(outcomes, outdir):
    fd = open(os.path.join(outdir, "graph.cypher"), "w")

    fd.write("CREATE ")
    seen = set()

    # Keep track of uids for nodes
    uids = {}

    def generate_placeholder(uids):
        while True:
            name = "".join(
                secrets.choice(string.ascii_letters) for i in range(8)
            ).lower()
            if name not in uids:
                return name

    # Create nodes first
    for package, results in outcomes.items():
        if package not in seen:
            seen.add(package)
            if package not in uids:
                uids[package] = generate_placeholder(uids)
            fd.write(
                "(%s:PACKAGE {name: '%s', label: '%s'}),\n"
                % (uids[package], package, package)
            )
        for splice, _ in results.items():
            if splice not in seen:
                seen.add(splice)
                if splice not in uids:
                    uids[splice] = generate_placeholder(uids)
                fd.write(
                    "(%s:PACKAGE {name: '%s', label: '%s'}),\n"
                    % (uids[splice], splice, splice)
                )

    # Next create edges
    text = ""
    for package, entries in outcomes.items():
        for splice, results in entries.items():
            if results["success"] != 0:
                text += "(%s)-[:PREDICT_SUCCESS_%s]->(%s),\n" % (
                    uids[splice],
                    results["success"],
                    uids[package],
                )
            if results["failure"] != 0:
                text += "(%s)-[:PREDICT_FAILURE_%s]->(%s),\n" % (
                    uids[splice],
                    results["failure"],
                    uids[package],
                )

    text = text.strip(",\n")
    fd.write(text + ";\n")
    fd.close()


def get_outcomes(experiments):

    # Total counts of predictions for each predictor
    outcomes = {}
    for filename, exps in experiments.items():
        for exp in exps:
            splice = exp["splice"]
            package = exp["package"]
            if (
                exp["result"] == "splice-success"
                and exp["predictions"]
                and "libabigail" in exp["predictions"]
            ):
                for pred in exp["predictions"]["libabigail"]:
                    if package not in outcomes:
                        outcomes[package] = {}
                    if splice not in outcomes[package]:
                        outcomes[package][splice] = {"success": 0, "failure": 0}
                    if pred["prediction"] == True:
                        outcomes[package][splice]["success"] += 1
                    else:
                        outcomes[package][splice]["failure"] += 1
    return outcomes


if __name__ == "__main__":
    main()
