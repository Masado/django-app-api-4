#!/usr/bin/env python3

import sys
import os
import json

if len(sys.argv) < 3:
    print("Merge the contents of many files into one JS object, with filenames (minus extension) as keys.")
    print("The output is printed to stdout.\n")
    print("Usage: merge_to_js_object.py <output variable name> <files to insert>...")

output_name = sys.argv[1]

entries = {}

for filename in sys.argv[2:]:
    name = os.path.splitext(filename)[0]

    with open(filename, "r") as f:
        entries[name] = f.read()

js_object = json.dumps(entries)
content = "var " + output_name + " = " + js_object + ";"

print(content)

