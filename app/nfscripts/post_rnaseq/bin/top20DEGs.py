#!/usr/bin/env python3

import argparse
import csv
from os import path as op

#./top20DEGs.py --deseq ../schusser_chicken/results_singleEnd_salmon_severalInput_complete/deseq2/transcript_id/*.csv

parser = argparse.ArgumentParser()
parser.add_argument('--deseq', nargs='+')
args = parser.parse_args()

out = {}
id_cnt = 0
for f in args.deseq:
	print ("reading " + op.basename(str(f)) + " ...")
	with open(f) as csv_file:
		file_name = op.basename(str(f)).replace(".csv", "")
		r = csv.reader(csv_file, delimiter=',')
		cnt = 0
		out[file_name] = {}
		for line in r:
			if cnt > 0:
				ensembl_id = line[0]
				if not line[2] == "NA":
					out[file_name][ensembl_id] = {"l2FC" : float(line[2]), "lfcSE" : line[3] if line[3] == "NA" else float(line[3]), "pvalue" : line[5] if line[5] == "NA" else float(line[5])}
			cnt += 1

for fn in out.keys():
	print ("\n" + str(fn) + "\nGeneID\tl2FC\tpvalue\tGeneID\tl2FC\tpvalue")
	up_sort = {k: v for k, v in sorted(out[fn].items(), key=lambda item: item[1]["l2FC"], reverse=True)}
	down_sort = {k: v for k, v in sorted(out[fn].items(), key=lambda item: item[1]["l2FC"], reverse=False)}
	up20 = []
	down20 = []
	cnt = 0
	for k in up_sort:
		if cnt == 20:
			break
		if not up_sort[k]["pvalue"] == "NA" and up_sort[k]["pvalue"] <= 0.01:
			up20.append([k, up_sort[k]])
			cnt += 1
	cnt = 0
	for k in down_sort:
		if cnt == 20:
			break
		if not down_sort[k]["pvalue"] == "NA" and down_sort[k]["pvalue"] <= 0.01:
			down20.append([k, down_sort[k]])
			cnt += 1
	for i in range(0, 20):
		print (str(up20[i][0]) + "\t" + str(round(up20[i][1]["l2FC"], 2)) + "\t" + str(up20[i][1]["pvalue"]) + "\t" + str(down20[i][0]) + "\t" + str(round(down20[i][1]["l2FC"], 2)) + "\t" + str(down20[i][1]["pvalue"]))


print ("\n\nUse the Force Luke!")
