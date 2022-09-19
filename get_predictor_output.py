#!/usr/bin/env python3

import argparse
import json
import sys
import os

# usage
# All predictors
# python get_predictor_output.py artifacts/results/extracted/fedora/usr/lib64/krb5/plugins/tls/k5tls-fedora-libs-34-fedora-libs-35.json

# Show command too
# python get_predictor_output.py artifacts/results/extracted/fedora/usr/lib64/krb5/plugins/tls/k5tls-fedora-libs-34-fedora-libs-35.json --command

# A specific one
# python get_predictor_output.py artifacts/results/extracted/fedora/usr/lib64/krb5/plugins/tls/k5tls-fedora-libs-34-fedora-libs-35.json libabigail

predictors = ["smeagle", "libabigail", "symbols", "abi-laboratory"]


def read_file(filename):
    """
    Read content from file
    """
    with open(filename, "r") as fd:
        content = fd.read()
    return content


def read_json(filename):
    with open(filename, "r") as fd:
        content = json.loads(fd.read())
    return content


def get_parser():
    parser = argparse.ArgumentParser(
        description="Get predictor output message",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("path", help="full path to the result file (json)")
    parser.add_argument(
        "--command",
        help="print the command too (or symbols type)",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "predictor",
        help="the predictor to get a result message for",
        nargs="?",
        default=predictors,
    )
    return parser


def main():

    parser = get_parser()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    if isinstance(args.predictor, str):
        args.predictor = [args.predictor]

    # Show args to the user
    print("       path: %s" % args.path)
    print(" predictors: %s\n" % args.predictor)

    if not os.path.exists(args.path):
        sys.exit(f"{args.path} does not exist.")
    result = read_json(args.path)

    for res in result:
        for p in args.predictor:
            if p not in res["predictions"]:
                print(f"WARNING: {p} is not a known predictor for this result.")
                continue
            print(f"============== {p} ============== ")
            for r in res["predictions"][p]:
                if args.command:
                    print(r["command"])
                if "message" in r and r["message"]:
                    print(r["message"])
                else:
                    print("<no message>")


if __name__ == "__main__":
    main()
