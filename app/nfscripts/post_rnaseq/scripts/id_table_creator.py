#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input')
parser.add_argument('--out')
args = parser.parse_args()

out = {}
#cnt = 0
with open(args.input) as file:
	for line in file:
		c = line.split()
#		print (c)
#		print (c[9][1:-2] + "\t" + c[13][1:-2] + "\t" + c[27][1:-2])
		if c[2] == "CDS":
			if c[27][1:-2] == "ensembl":
#				print (c[31])
#				cnt += 1
				if c[13][1:-2] not in out:
					out[c[13][1:-2]] = {"gene_id": c[9][1:-2], "protein_id": c[31][1:-2]}
				elif not c[31][1:-2] == out[c[13][1:-2]]["protein_id"]:
					print (out[c[13][1:-2]])
					print (c[13][1:-2] + "\t" + c[31][1:-2] + "\n")
			else:
				if c[13][1:-2] not in out:
					out[c[13][1:-2]] = {"gene_id": c[9][1:-2], "protein_id": c[27][1:-2]}
				elif not c[27][1:-2] == out[c[13][1:-2]]["protein_id"]:
					print (out[c[13][1:-2]])
					print (c[13][1:-2] + "\t" + c[27][1:-2] + "\n")
			

with open(args.out, 'w') as outfile:
	for k in out.keys():
		outfile.write(str(k) + "\t" + out[k]["protein_id"] + "\t" + out[k]["gene_id"] + "\n")

print ("\n\nUse the Force Luke!")
