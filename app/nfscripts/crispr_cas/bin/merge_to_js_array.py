#!/usr/bin/env python3

import sys

name = sys.argv[1]

content = "var " + name + " = ["

for filename in sys.argv[2:]:
    with open(filename, "r") as f:
        content += "`" + f.read() + "`,"
content += "];"

print(content)

