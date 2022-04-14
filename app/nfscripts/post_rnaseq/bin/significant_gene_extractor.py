#!/usr/bin/env python3

import argparse
import csv

#./significant_gene_extractor.py --deseq GFE2C1_vs_GFE2C2.csv --out GFE2C1_vs_GFE2C2_significant.txt

parser = argparse.ArgumentParser()
parser.add_argument('--deseq')
parser.add_argument('--out')
args = parser.parse_args()

if not args.deseq:
	print ("No deseq data provided!")
	print ("\n\nUse the Force Luke!")
	exit(0)

if not args.out:
	print ("No output file specified!")
	print ("\n\nUse the Force Luke!")
	exit(0)

pv_threshold = 0.01
lfc_threshold = 1

out = {}
id_cnt = 0
f = args.deseq
print ("reading " + str(f) + " ...")
with open(f) as csv_file:
	r = csv.reader(csv_file, delimiter=',')
	cnt = 0
	for line in r:
		if cnt > 0:
			ensembl_id = line[0]
			if ensembl_id in out:
				out[ensembl_id][str(f)] = {"l2FC" : 0.0 if line[2] == "NA" else float(line[2]), "lfcSE" : 0.0 if line[3] == "NA" else float(line[3]), "pvalue" : 0.0 if line[5] == "NA" else float(line[5])} # is it legit to convert "NA" to 0.0?
			else:
				out[ensembl_id] = {str(f) : {"l2FC" : 0.0 if line[2] == "NA" else float(line[2]), "lfcSE" : 0.0 if line[3] == "NA" else float(line[3]), "pvalue" : 0.0 if line[5] == "NA" else float(line[5])}} # is it legit to convert "NA" to 0.0?
		cnt += 1

with open(args.out, 'w') as outfile:
	for gene in out.keys():
		if out[gene][f]["pvalue"] <= float(pv_threshold) and (out[gene][f]["l2FC"] >= float(lfc_threshold) or out[gene][f]["l2FC"] <= float(lfc_threshold)*(-1)):
			outfile.write(str(gene) + "\n")


print ("\n\nUse the Force Luke!")
