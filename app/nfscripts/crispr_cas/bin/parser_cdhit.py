#!/usr/bin/env python3

import argparse
import os
import json

parser = argparse.ArgumentParser(description="parser, der ein dictionary mit den Namen der spacer erstellt")
parser.add_argument("-inp,", "--input", dest="inp", nargs="*", default=[], help="Insert "
                    "CD-Hit-output Files to create a dictionary of the inserted species and their spacers")
args = parser.parse_args()


def main():
    # Input: CD-Hit Output Datei
    if args.inp:
        cluster_dic = {}
        name_dic = {}
        for file in args.inp:
            # Überprüfen, ob Datei existiert und nicht leer ist.
            if os.path.exists(file):
                if not os.stat(file).st_size == 0:
                    with open(file, "r") as input_file:
                        for line in input_file:
                            line = line.split()
                            if line:
                                # Sucht alle Zeilen heraus, die mit ">Cluster" beginnen und sortiert diese in ein
                                # Dictionary ein, mit einer leeren Liste als Value
                                if line[0] == ">Cluster":
                                    cluster_name = line[1]
                                    cluster_dic[cluster_name] = []

                                # Wenn die Zeile mit einer Zahl beginnt, wird die Value-Liste des Dictionaries für
                                # den jeweiligen Key mit der NC-Nummer des jeweiligen Spacers im Cluster gefüllt.
                                if line[0].isdigit():
                                    nc_name = line[2][1:-3]
                                    cluster_dic[cluster_name].append(nc_name)
                                    name_dic[nc_name] = cluster_name
                else:
                    print("Error: the inserted file is empty")
            else:
                print("Error: the given path isinvalid or the file doesn't exist")
        # Abschließend wird das Dictionary in eine JavaScript Datei geschrieben, um es in die HTML einbinden zu können.
        msa_name_dic = json.dumps(name_dic)
        msa_cluster_dic = json.dumps(cluster_dic)
        with open("parsed_cdHit_output.js", "w+") as parsed_file:
            parsed_file.write("var spacerToCluster = " + msa_name_dic + ";\n")
            parsed_file.write("var clusterSpacers = " + msa_cluster_dic + ";\n")
    else:
        print("Error: No file was inserted")


if __name__ == '__main__':
    main()

