#!/usr/bin/env python3

import argparse
import os
from Bio.Blast import NCBIXML

parser = argparse.ArgumentParser(description="Command line tool to parse Querys and hits from blastn(BLAST) Output "
                                             "into fasta files")
parser.add_argument("-inp", "--input", dest="inp", nargs="*", default=["blastedSpacer.xml"],
                    help="Insert blastn output file (Default=\"\")")
args = parser.parse_args()


def main():
    if args.inp:
        for f in args.inp:
            file = f
            if os.path.exists(file):
                if not os.stat(file).st_size == 0:

                    blast_output_index = open(file, "r")

                    blast_output = NCBIXML.parse(blast_output_index)
                    blast_output = list(blast_output)

                    for blastQuery in blast_output:

                        query_name = blastQuery.query.split()
                        with open(query_name[1] + ".fna", "w+") as fastaToWrite:
                            fastaToWrite.write(">" + query_name[1])

                        for alignment in blastQuery.alignments:
                            for hsp in alignment.hsps:

                                n=0
                                if n == 0:
                                    query_seq = hsp.query
                                    with open(query_name[1] + ".fna", "a") as myFile1:
                                        myFile1.write("\n" + query_seq)
                                    n += 1
                                align_name = alignment.title.split()
                                align_seq = hsp.sbjct
                                with open(query_name[1] + ".fna", "a") as myFile2:
                                    myFile2.write("\n" + ">" + align_name[1] + "\n" + align_seq)





                else:
                    print("File is empty or not usable 1. Please check that.")
            else:
                print("File is empty or not usable 2. Please check that.")
    else:
        print("File is empty or not usable 3. Please check that.")

if __name__ == '__main__':
    main()
