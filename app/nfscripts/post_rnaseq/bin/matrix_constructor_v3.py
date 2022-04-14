#!/usr/bin/env python3

import argparse
import csv

#./matrix_constructor.py --deseq *.csv --species 9823 --out pig_deseq_indicator_matrix_extended.txt

parser = argparse.ArgumentParser()
parser.add_argument('--deseq', nargs='+')
parser.add_argument('--species')
#parser.add_argument('--threshold') # 1 for l2FC and 0.01-0.1 for pvalue
parser.add_argument('--ids')
parser.add_argument('--out')
args = parser.parse_args()

if not args.deseq:
	print ("No deseq data provided!")
	print ("\n\nUse the Force Luke!")
	exit(0)

if not args.species:
	print ("No species ID provided!")
	print ("\n\nUse the Force Luke!")
	exit(0)

if not args.out:
	print ("No output file specified!")
	print ("\n\nUse the Force Luke!")
	exit(0)

ids = {}
if args.ids:
	with open(args.ids) as id_file:
		for line in id_file:
			c = line.split()
			ids[c[0]] = {"protein_id": c[1], "gene_id": c[2]}

pv_threshold = 0.01
lfc_threshold = 1

out = {}
id_cnt = 0
for f in args.deseq:
	print ("reading " + str(f) + " ...")
	with open(f) as csv_file:
		r = csv.reader(csv_file, delimiter=',')
		cnt = 0
		for line in r:
			if cnt > 0:
				ensembl_id = line[0]
				if args.ids:
					if ensembl_id in ids:
						ensembl_id = ids[ensembl_id]["protein_id"]
						if ensembl_id in out:
							out[ensembl_id][str(f)] = {"l2FC" : 0.0 if line[2] == "NA" else float(line[2]), "lfcSE" : 0.0 if line[3] == "NA" else float(line[3]), "pvalue" : 0.0 if line[5] == "NA" else float(line[5])}
						else:
							out[ensembl_id] = {str(f) : {"l2FC" : 0.0 if line[2] == "NA" else float(line[2]), "lfcSE" : 0.0 if line[3] == "NA" else float(line[3]), "pvalue" : 0.0 if line[5] == "NA" else float(line[5])}}
				else:
					if ensembl_id in out:
						out[ensembl_id][str(f)] = {"l2FC" : 0.0 if line[2] == "NA" else float(line[2]), "lfcSE" : 0.0 if line[3] == "NA" else float(line[3]), "pvalue" : 0.0 if line[5] == "NA" else float(line[5])} # is it legit to convert "NA" to 0.0?
					else:
						out[ensembl_id] = {str(f) : {"l2FC" : 0.0 if line[2] == "NA" else float(line[2]), "lfcSE" : 0.0 if line[3] == "NA" else float(line[3]), "pvalue" : 0.0 if line[5] == "NA" else float(line[5])}} # is it legit to convert "NA" to 0.0?
			cnt += 1

with open(args.out, 'w') as outfile:
	for gene in out.keys():
		outfile.write(str(args.species)+ "." + str(gene) + "\t")
		for f in args.deseq:
			outfile.write(str(1 if out[gene][f]["pvalue"] <= float(pv_threshold) and (out[gene][f]["l2FC"] >= float(lfc_threshold) or out[gene][f]["l2FC"] <= float(lfc_threshold)*(-1)) else 0))
			if not f == args.deseq[-1]:
				outfile.write("\t")
		outfile.write("\n")


print ("\n\nUse the Force Luke!")
