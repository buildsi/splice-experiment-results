#!/usr/bin/env python3

import json
import sys

if len(sys.argv) != 2:
    print("Usage: read_errors.py file")
    exit()

with open(sys.argv[1], "r") as fd:
    res = json.loads(fd.read())[0]


for p in res["predictions"]:
    for r in res["predictions"][p]:
        if "message" in r and r["message"]:
            msg = r["message"]
            if isinstance(msg, list):
                msg = " ".join(msg)
            print("{0}:{1}\n".format(p, r["prediction"]), msg)
