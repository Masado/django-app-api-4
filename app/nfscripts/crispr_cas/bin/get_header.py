#!/usr/bin/env python3
from argparse import ArgumentParser
import os

parser = ArgumentParser(description="Command line tool to parse blast output (blastn) Output")


parser.add_argument("-inp", "--input", dest="inp", nargs="*", default=[],
                    help="Insert crt output file(s) (Default=\"\")")


parser.add_argument("-out", "--output", type=str, dest="out", default="",
                    help="Insert name for parser output file with no ending (Default=\"\")")

args = parser.parse_args()


def main():
    # Input: Crispr-Recognition-Tool Output Dateien.
    # Output: Dateiname ohne Dateiendung.
    if args.inp and args.out:
        dictionary = {}
        for i in args.inp:
            file = i
            # Überprüfung ob Datei existiert und ob Datei nicht leer ist.
            if os.path.exists(file):
                if not os.stat(file).st_size == 0:
                    with open(file, "r") as f:
                        header = f.readline()
                        if header:
                            nc_number = header.split()[1]
                            rest = " ".join(header.split()[2:])
                            dictionary[nc_number] = rest
                else:
                    print("File is empty or not usable. Please check that.")
            else:
                print("File doesn't exist. Please check that.")
        # Alle Header mit NC-Nummer und Name des Bakteriums werden in eine JavaScript Datei geschrieben
        # welche in die HTML eingebunden wird.
        with open(args.out + ".js", "w") as fl:
            fl.write("var headers = " + str(dictionary) + ";")
    else:
        print("No input file given. Please check that.")
    pass


if __name__ == '__main__':
    main()
