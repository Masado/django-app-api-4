#!/usr/bin/env python3

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--input')
parser.add_argument('--output')
args = parser.parse_args()

if not args.output:
	print("No output directory provided)
	exit(0)
	
if args.input:
    	string = args.input
    	splitString = string.split()
    	letterOne = splitString[0][0].lower()
    	outputString = (letterOne + splitString[1])	
    	
    	with open(args.output, 'w') as outFile:
		outFile.write(outputString)


