#!/usr/bin/env python3

import xml.etree.ElementTree as ET

## original spacer sequences, since blast result only contains the aligned part
spacers = {}
with open("mergedSpacers.fna") as f:
    for line in f:
        line = line.strip()
        if line:
            if line.startswith(">"):
                header = line[1:]
            else:
                spacers[header] = line

## blast results in XML format
tree = ET.parse("blastedSpacer.xml")
root = tree.getroot()

## list of query iterations
entries = root.findall("./BlastOutput_iterations/Iteration")

for iteration in entries:
    spacer = iteration.find("./Iteration_query-def").text
    fullSpacer = spacers[spacer]
    with open(spacer + ".fna", "w") as output:
        output.write(">" + spacer + "\n" + fullSpacer + "\n")
        hits = iteration.find("./Iteration_hits")
        for hit in hits.findall("./Hit"):
            hitName = hit.find("./Hit_def").text
            hitSeq = hit.find("./Hit_hsps/Hsp/Hsp_hseq").text
            output.write(">" + hitName + "\n" + hitSeq + "\n")


