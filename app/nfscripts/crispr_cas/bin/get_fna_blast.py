#!/usr/bin/env python3

from argparse import ArgumentParser
from Bio.Blast import NCBIXML

parser = ArgumentParser(description="Command line tool to get fna files from blast output for clustalw")


parser.add_argument("-inp", "--input", type=str, dest="inp", default="",
                    help="Insert blast output file in XML-Format (Default=\"\")")

args = parser.parse_args()


def main():
    if args.inp:
        if args.inp.split(".")[-1] == "xml":
            file = args.inp
            handle = open(file, "r")
            parsed_blast_output = parse_blast(handle)
            n = 0
            for i in parsed_blast_output:
                d = {}
                for query in i:
                    query_name = query
                    for subject in i[query]:
                        sbjct_name = subject
                        q_seq = i[query][subject][0]
                        s_seq = i[query][subject][1]
                        if q_seq in d.keys():
                            d[q_seq].append(sbjct_name)
                            d[q_seq].append(s_seq)
                        else:
                            d[q_seq] = [sbjct_name]
                            d[q_seq].append(s_seq)
                        for key in d:
                            n += 1
                            with open(query_name + "_" + str(n) + ".fna", "w") as fna_file:
                                fna_file.write(">" + query_name + " QUERY" + "\n")
                                fna_file.write(key + "\n")
                                m = 0
                                for seq in d[key]:
                                    if m % 2 == 0:
                                        fna_file.write(">" + seq + " HIT" + "\n")
                                    else:
                                        fna_file.write(seq + "\n")
                                    m += 1

        else:
            print("Input file isn't a xml file. Please check that.")
    else:
        print("No input file given. Please check that.")


def parse_blast(handle):
    complete_list = []
    blast_records = NCBIXML.parse(handle)
    blast_records = list(blast_records)
    for blast_record in blast_records:
        n = 0
        dict_qname_values = {}
        dictionary_key_value = {}
        subjects = []
        query_alignments = []
        sbjct_alignments = []

        query = blast_record.query.split()[1]
        for des in blast_record.descriptions:
            n += 1
            subjects.append(str(des).split()[1])
        for al in blast_record.alignments:
            for hsp in al.hsps:
                query_alignments.append(hsp.query)
                sbjct_alignments.append(hsp.sbjct)

        if n > 0:
            for i in range(n):
                dictionary_key_value[subjects[i]] = [query_alignments[i], sbjct_alignments[i]]
            dict_qname_values[query] = dictionary_key_value
            complete_list.append(dict_qname_values)

    return complete_list


if __name__ == '__main__':
    main()
