#!/usr/bin/env python3

import argparse
import os
from Bio import AlignIO
from Bio.Align import AlignInfo

parser = argparse.ArgumentParser(description="Parser, der repeats jedes Organismus aus dem CRT output zu einem "
                                             "consensus vereint und in fasta Dateien zusammenführt")
parser.add_argument("-inp", "--input", dest="inp", nargs="*", default=[],
                    help="Insert CRT-output files to parse ""(Default=\"\")")
args = parser.parse_args()


def main():
    if args.inp:
        n = 0
        consensus_dic = {}
        spacer_dic = {}
        repeat_dic = {}
        for file in args.inp:
            n += 1
            if os.path.exists(file):
                if not os.stat(file).st_size == 0:

                    consensus_dic, spacer_dic = get_consensus(file, n,  consensus_dic, spacer_dic)

                else:
                    print("Input file is empty. Please check that")
            else:
                print("Input file doesn't exist. Please check that.")
        key_list = []
        match_list = []
        for key1 in consensus_dic:
            seq1_repeat = consensus_dic[key1]
            key1_dic = {key1: []}
            key_list.append(key1)
            for key2 in consensus_dic:
                if key2 not in key_list:
                    if key1 != key2:
                        seq2_repeat = consensus_dic[key2]
                        key2_dic = {key2: []}
                        score_consensus = needle(seq1_repeat, seq2_repeat)
                        if score_consensus.isdigit():
                            spacer_key1 = spacer_dic[key1]
                            spacer_key2 = spacer_dic[key2]
                            spacer_key_list = []
                            for spacer1 in spacer_key1:
                                for spacer2 in spacer_key2:
                                    if spacer2 not in spacer_key_list:
                                        score_spacer = needle(spacer1, spacer2)
                                        if score_spacer.isdigit():
                                            key1_dic[key1].append(spacer1)
                                            key2_dic[key2].append(spacer2)
                                spacer_key_list.append(spacer1)
                            if len(key1_dic[key1]) and len(key2_dic[key2]):
                                match_list.append([key1_dic, key2_dic])

        repeat_dic = get_repeat_dic(repeat_dic, spacer_dic, consensus_dic)
        for key in repeat_dic:
            file_name = key
            with open(file_name + "_con.fasta", "w+") as consensus_file:
                for dic in repeat_dic[key]:
                    organism_name = dic
                    for spacer in repeat_dic[key][dic]:
                        spacer_seq = spacer
                        consensus_file.write(">" + organism_name + "\n")
                        consensus_file.write(spacer_seq + "\n")
    else:
        print("No input file given. Please check that.")


def get_consensus(file, n,  consensus_dic, spacer_dic):
    with open(file, "r") as input_file:
        for line in input_file:
            line = line.split()
            if line:
                if line[0] == "ORGANISM:":
                    organism_name = line[1] + "_" + str(n)

                if line[0] == "CRISPR" and line[1].isdigit():
                    crispr_num = "_".join(line[0:2])
                    spacer_seq_list = []
                    open("calculate_consensus.fasta", "w+")

                if line[0].isdigit() and not line[1].isdigit():
                    repeat_seq = line[1]
                    with open("calculate_consensus.fasta", "a+") as f:
                        f.write(">" + organism_name + "\n")
                        f.write(repeat_seq + "\n")

                    if len(line) > 2:
                        spacer_seq = line[2]
                        spacer_seq_list.append(spacer_seq)

                if line[0] == "Repeats:":
                    alignment = AlignIO.read("calculate_consensus.fasta", 'fasta')
                    summary_align = AlignInfo.SummaryInfo(alignment)
                    consensus = summary_align.gap_consensus(threshold=0.5)
                    consensus_dic[organism_name + "_" + crispr_num] = str(consensus)
                    spacer_dic[organism_name + "_" + crispr_num] = spacer_seq_list

    return consensus_dic, spacer_dic


def get_repeat_dic(repeat_dic, spacer_dic, consensus_dic):
    for key in consensus_dic:
        consensus = consensus_dic[key]
        consensus_name = key
        for key_spacer in spacer_dic:
            if key_spacer == consensus_name:
                spacer_list = spacer_dic[key_spacer]
                spacer_name = key_spacer

                dic_dic = {spacer_name: spacer_list}

                if consensus in repeat_dic.keys():
                    repeat_dic[consensus].update(dic_dic)
                else:
                    repeat_dic[consensus] = dic_dic
    return repeat_dic


def needle(s1, s2):
    penalties = {"MATCH": 1, "MISMATCH": -1, "GAP": -2}

    rows = len(s1) + 1
    cols = len(s2) + 1

    mat = [[0] * cols for e in range(rows)]

    for i in range(0, rows):
        mat[i][0] = penalties["GAP"] * i

    for j in range(0, cols):
        mat[0][j] = penalties["GAP"] * j

    for i in range(1, rows):
        for j in range(1, cols):
            diagonal = mat[i - 1][j - 1] + matches(s1[i - 1], s2[j - 1], penalties)
            horizontal = mat[i][j - 1] + penalties["GAP"]
            vertical = mat[i - 1][j] + penalties["GAP"]
            mat[i][j] = max(diagonal, horizontal, vertical)

    score = mat[rows - 1][cols - 1]

    if len(s1) >= len(s2):
        max_score = len(s2)*penalties["MATCH"]
    else:
        max_score = len(s1)*penalties["MATCH"]

    if score >= max_score*0.95:
        return str(score)
    else:
        return "Score insufficient"


def matches(c1, c2, penalties):
    if c1 == c2:
        return penalties["MATCH"]
    else:
        return penalties["MISMATCH"]


if __name__ == '__main__':
    main()