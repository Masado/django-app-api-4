#!/usr/bin/env python3

import argparse
import os

parser = argparse.ArgumentParser(description="Command line tool to parse blastn (BLAST) Output")
parser.add_argument("-inp", "--input", dest="inp", nargs="*", default=["testnames.txt"], help="Insert unzipped file of names (Default=\"\")")
parser.add_argument("-out", "--output", type=str, dest="out", default="TEST",help="Insert name for output file (Default=\"\")")
args = parser.parse_args()

def main():
	if args.inp:
		for f in args.inp:
			file = f
			if os.path.exists(file):
				if not os.stat(file).st_size == 0:

					with open(args.out + ".txt", "w") as f:
						f.write(str(get_names(file)))
				else:
					print("File is empty or not usable. Please check that.")
			else:
				print("File is empty or not usable. Please check that.")
	else:
		print("File is empty or not usable. Please check that.")

def get_names(file):
	with open(file, "r") as name_file:

		name_dict = {}
		for line in name_file:
			line = line.split()
			print(line)
			if line:
				nc_key = line[0]
				name_value = " ".join(line[1:])
				name_dict[nc_key] = name_value

	return name_dict


if __name__ == '__main__':
    main()
