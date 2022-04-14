import gtfparse.parsing_error
import pandas as pd
from pandas.api.types import is_numeric_dtype
from gtfparse import read_gtf
from Bio import SeqIO
import os
from django.shortcuts import render, redirect


def check_rnaseq_samplesheet(df):
    if os.stat(df).st_size == 0:
        return False
    c = pd.read_csv(df)
    if not check_csv(c, 4):
        return False
    headers = c.columns.values
    if headers[0] != "sample" or headers[1] != "fastq_1" or headers[2] != "fastq_2" or headers[3] != "strandedness":
        return False
    return True


def check_atacseq_design(df):
    if os.stat(df).st_size == 0:
        return False
    c = pd.read_csv(df)
    if not check_csv(c, 4):
        return False
    headers = c.columns.values
    if headers[0] != "group" or headers[1] != "replicate" or headers[2] != "fastq_1" or headers[3] != "fastq_2":
        return False
    return True


def check_chipseq_design(df):
    if os.stat(df).st_size == 0:
        return False
    c = pd.read_csv(df)
    if not check_csv(c, 6):
        return False
    headers = c.columns.values
    if headers[0] != "group" or headers[1] != "replicate" or headers[2] != "fastq_1" or headers[3] != "fastq_2" \
            or headers[4] != "antibody" or headers[5] != "control":
        return False
    return True


def check_sarek_design(df):
    if os.stat(df).st_size == 0:
        return False
    return True


def check_bed(df):
    if os.stat(df).st_size == 0:
        return False
    bed = pd.read_csv(df, sep='\t', comment="t", header=None)
    if bed.shape[1] != 12:
        return False
    if not is_numeric_dtype(bed[1]) or not is_numeric_dtype(bed[2]) or not is_numeric_dtype(bed[6]) or not \
            is_numeric_dtype(bed[7]):
        return False
    bed[5] = bed[5].fillna(0)
    if len(bed[5].unique()) > 3:
        return False
    return True


def check_gtf(df):
    if os.stat(df).st_size == 0:
        return False
    gtf = load_gtf(df)
    # if not gtf:
    #     return False

    # gtf = pd.read_csv(df, sep="\t", header=None)
    if len(gtf["strand"].unique()) > 2:
        return False
    return True


def check_fasta(df):
    if os.stat(df).st_size == 0:
        return False
    with open(df) as f:
        fasta = SeqIO.parse(f, "fasta")
        return any(fasta)


def check_csv(df, cols):
    if df.shape[1] != cols:
        return False
    else:
        return True


def load_gtf(df):
    try:
        gtf = read_gtf(df)
        return gtf
    except ValueError:
        # return False
        return redirect("run:inputProblems", "gtf")
    except gtfparse.parsing_error.ParsingError:
        # return False
        return redirect("run:inputProblems", "gtf")