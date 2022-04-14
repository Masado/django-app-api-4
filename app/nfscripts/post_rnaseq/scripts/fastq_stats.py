#!/usr/bin/env python3

import argparse
import os
import ntpath
from Bio import SeqIO

parser = argparse.ArgumentParser()
parser.add_argument('--fasta', nargs='+')
parser.add_argument('--fastq', nargs='+')
parser.add_argument('--out')
args = parser.parse_args()


if args.fastq or args.fasta:
	files = []
	t = ""
	if args.fasta:
		files = args.fasta
		t = "fasta"
	if args.fastq:
		files = args.fastq
		t = "fastq"
	for f in files:
		total_len = 0
		min_len = 0
		max_len = 0
		cnt_r = 0
		print ("\nreading " + ntpath.basename(f) + " ...")
		for record in SeqIO.parse(f, t):
			if cnt_r == 0:
				min_len = len(record.seq)
				max_len = len(record.seq)
			cnt_r += 1
			total_len += len(record.seq)
			if len(record.seq) < min_len:
				min_len = len(record.seq)
			if len(record.seq) > max_len:
				max_len = len(record.seq)
		print ("#reads=" + str(cnt_r) + "\ttotal=" + str(total_len) + "\tavg=" + str(total_len/cnt_r) + "\tmin=" + str(min_len) + "\tmax=" + str(max_len))

if args.out:
	with open(args.out, 'w') as outfile:
		json.dump(out, outfile, indent=4)

print ("\n\nUse the Force Luke!")
