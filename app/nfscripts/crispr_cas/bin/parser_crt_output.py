#!/usr/bin/env python3

import os
from argparse import ArgumentParser

parser = ArgumentParser(description="Command line tool to parse CRISPR Recognition Tool (crt) Output")

parser.add_argument("-inp", "--input", dest="inp", nargs="*", default=[],
                    help="Insert crt output file (Default=\"\")")

parser.add_argument("-gs", "--get_spacer", dest="gs", type=bool, default=False,
                    help="Get fasta files with all spacer in input file (Default=False)")

parser.add_argument("-gr", "--get_repeats", dest="gr", type=bool, default=False,
                    help="Get repeats per detected CRISPR cas in input file (Default=False)")

parser.add_argument("-gcc", "--get_crispr_cas", dest="gcc", type=bool, default=False,
                    help="Get crispr cassets from repeats and spacer (Default=False)")

args = parser.parse_args()


def main():
    # Input: Crisper-Recognition-Tool (CRT) Output Dateien
    if args.inp:
        for i in args.inp:
            file = i
            # Überprüfen, ob Datei existiert und nicht leer ist.
            if os.path.exists(file):
                if not os.stat(file).st_size == 0:
                    dictionary, header = crt_output_parse(file)

                    # Wenn eingegebene Parameter auf True gesetzt werden, werden spezifische Teile aus dem Input
                    # herausgeholt. Spacer, Repeats oder ganze Crisper-Kassetten
                    # Diese werden dann jeweils in eigene Dateien geschrieben, womit weitergearbeitet werden kann.
                    if args.gs:
                        get_spacer(dictionary, header)

                    if args.gr:
                        get_repeats(dictionary, header)

                    if args.gcc:
                        get_crispr_cas(dictionary, header)
                else:
                    print("File is empty or not usable. Please check that.")
            else:
                print("File doesn't exist. Please check that.")
    else:
        print("No input file given. Please check that.")


def crt_output_parse(file):
    with open(file, "r") as f:
        crisprLoci = []
        organism = f.readline().split()[1]
        for line in f:
            line = line.split()
            if line:
                if line[0] == "CRISPR":
                    crisprLoci.append({"repeats": [], "spacers": []})

                if line[0].isdigit():
                    crisprLoci[-1]["repeats"].append(line[1])
                    if len(line) > 2:
                        crisprLoci[-1]["spacers"].append(line[2])
    return crisprLoci, organism


# Repeats werden mit Organismus-Namen und Repeat-Nummer in eine Datei geschrieben.
def get_repeats(crisprLoci, organism):
    for locus, content in enumerate(crisprLoci):
        with open(organism + "_CRISPR_" + str(locus) + "_repeats.fasta", "w") as f:
            for index, repeat in enumerate(content["repeats"]):
                f.write(">" + organism + "_CRISPR_" + str(locus) + "_REPEAT_" + str(index) + "\n")
                f.write(repeat + "\n")


# Spacer werden mit Organismus-Name und Spacer-Nummer in eine Datei geschrieben.
def get_spacer(crisprLoci, organism):
    with open(organism + "_spacers.fasta", "w") as f:
        for locus, content in enumerate(crisprLoci):
            for index, spacer in enumerate(content["spacers"]):
                f.write(">" + organism + "_CRISPR_" + str(locus) + "_SPACER_" + str(index) + "\n")
                f.write(spacer + "\n")


# Die Crisper-Kassetten werden wieder zusammen gebaut. Repeats und Spacer werden zu einer Kassette zusammengebaut.
# Repeat-Spacer-Repeat-Spacer-Repeat...
def get_crispr_cas(crisprLoci, organism):
    for locus, content in enumerate(crisprLoci):
        with open(organism + "_CRISPR_" + str(locus) + "_crispr_cas.fasta", "w") as f:
            f.write(">" + organism + "_CRISPR_" + str(locus) + "\n")
            for index, repeat in enumerate(content["repeats"]):
                f.write(repeat)
                if index < len(content["spacers"]):
                    f.write(content["spacers"][index])
            f.write("\n")


if __name__ == '__main__':
    main()
