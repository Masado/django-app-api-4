#!/usr/bin/env python3

import os
from Bio import Phylo
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor
from argparse import ArgumentParser
import operator

parser = ArgumentParser(description="Command line tool to parse CRISPR Recognition Tool (crt) Output and retrieve"
                                    "arrays of spacer from cdhit clustering and create a distance tree"
                                    " out of the arrays.")

parser.add_argument("-inp_crt_out", "--input_crt_output", dest="inp1", nargs="*", default=[],
                    help="Insert crt output file (Default=\"\")")

parser.add_argument("-inp_cdhit_out", "--input_cdhit_output", dest="inp2", type=str,
                    default="", help="Insert cdhit output file. (with ending: clstr)")

args = parser.parse_args()


def main():
    # Input1: Crisper-Recognition-Tool (CRT) Output
    # Input2: CD-Hit Output
    if args.inp1 and args.inp2:
        allmighty_dic = {}
        for i in args.inp1:
            b_dic = {}
            file = i
            # Überprüfen, ob beide Dateien existieren und nicht leer sind.
            if os.path.exists(file) and os.path.exists(args.inp2):
                if not os.stat(file).st_size == 0 and not os.stat(args.inp2).st_size == 0:
                    # Spacer, Repeats, Organismus-Namen und Locus werden in einem Dictionary gespeichert
                    # Header pro Datei (mit NC-Nummer und Bakterien-Stamm) werden gespeichert
                    dictionary, header = crt_output_parse(file)
                    # Cluster werden geparsed um pro Cluster die Spacer zu bekommen (in einem Dictionary)
                    cluster_spacer_dic = parse_cluster(args.inp2)
                    # Spacer in Cluster werden in entsprechende Zahlen gewandelt, um zu sehen, welche Spacer sich
                    # ähnlich sind und zu einem Cluster gehören
                    b_dic = get_spacer_array_per_file(dictionary, cluster_spacer_dic)
                else:
                    print("File is empty or not usable. Please check that.")
            else:
                print("File doesn't exist. Please check that.")
            allmighty_dic.update(b_dic)
        # Aus den Arrays von Zahlen kann ein Phylogenetischer Baum erstellt werden, der in die HTML eingebunden wird.
        matrix_dic, names = compare_arrays2(allmighty_dic)
        build_matrix(matrix_dic, names)
    else:
        print("Missing input file. Please check that.")


def build_matrix(matrix_dic, names):
    constructor = DistanceTreeConstructor()
    matrix = []
    for dic in matrix_dic:
        for key in dic:
            dic[key].reverse()
            matrix.append(dic[key])
    names.reverse()
    matrix.reverse()
    m = DistanceMatrix(names, matrix)
    nj_tree = constructor.nj(m)

    Phylo.write(nj_tree, 'distanceTree.nwck', 'newick')

    with open('distanceTree.nwck', 'r') as nwck:
        tree_text = nwck.read()
    with open('distanceTree.js', 'w') as js:
        js.write('var distanceTree = `' + tree_text + '`;')


def compare_arrays2(all_dic):
    names = []
    c_dic = []
    z = []
    for key in all_dic:
        names.append(key)
        key_dic = {key: []}
        for i in all_dic:
            if {key: i} and {i: key} not in z:
                z.append({key: i})
                dist, _, _ = edit_distance_backpointer(all_dic[key], all_dic[i])
                key_dic[key].append(dist)
        c_dic.append(key_dic)

    return c_dic, names


def get_spacer_array_per_file(crt_out, cluster_spacer_dic):
    b_dic = {}
    for i in crt_out:
        original = i["organism"] + "_" + i["locus"]
        spacer_to_num = {original: []}
        name = original
        spacer = i["spacers"]
        n = 0
        for x in spacer:
            n += 1
            name = name + "_SPACER_" + str(n)
            for key in cluster_spacer_dic:
                if name in cluster_spacer_dic[key]:
                    spacer_to_num[original].append(key)
            name = original
        b_dic.update(spacer_to_num)
    return b_dic


def parse_cluster(file):
    spacer_cluster_dic = {}
    with open(file, "r") as f:
        for line in f:
            line = line.split()
            if line[0] == ">Cluster":
                clstr_num = line[1]
                spacer_cluster_dic[int(line[1])] = []
            else:
                new_value = line[2][:-3]
                new_value = new_value.split(">")[1]
                spacer_cluster_dic[int(clstr_num)].append(new_value)

    return spacer_cluster_dic


def crt_output_parse(file):
    with open(file, "r") as f:
        crisper_loci = []
        organism = f.readline().split()[1]
        for line in f:

            line = line.split()
            if line:
                if line[0] == "CRISPR":
                    crisper_loci.append({"spacers": [],
                                         "locus": "_".join(line[0:2]), "organism": organism})

                if line[0].isdigit():
                    if len(line) > 2:
                        crisper_loci[-1]["spacers"].append(line[2])
    return crisper_loci, organism


# Edit-Distanz-Berechnungs-Funktion aus dem Internet.
# "Zweckentfremdet" um zwei Arrays aus Zahlen miteinander zu vergleichen und die Distanz zu berechnen, woraus ein
# Phylogenetischer Baum erstellt wird.

# Copyright 2013-2018 Ben Lambert

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Code for computing edit distances.
"""

INSERT = 'insert'
DELETE = 'delete'
EQUAL = 'equal'
REPLACE = 'replace'


# Cost is basically: was there a match or not.
# The other numbers are cumulative costs and matches.

def lowest_cost_action(ic, dc, sc, im, dm, sm, cost):
    """Given the following values, choose the action (insertion, deletion,
    or substitution), that results in the lowest cost (ties are broken using
    the 'match' score).  This is used within the dynamic programming algorithm.
    * ic - insertion cost
    * dc - deletion cost
    * sc - substitution cost
    * im - insertion match (score)
    * dm - deletion match (score)
    * sm - substitution match (score)
    """
    best_action = None
    best_match_count = -1
    min_cost = min(ic, dc, sc)
    if min_cost == sc and cost == 0:
        best_action = EQUAL
        best_match_count = sm
    elif min_cost == sc and cost == 1:
        best_action = REPLACE
        best_match_count = sm
    elif min_cost == ic and im > best_match_count:
        best_action = INSERT
        best_match_count = im
    elif min_cost == dc and dm > best_match_count:
        best_action = DELETE
        best_match_count = dm
    return best_action


def highest_match_action(ic, dc, sc, im, dm, sm, cost):
    """Given the following values, choose the action (insertion, deletion, or
    substitution), that results in the highest match score (ties are broken
    using the distance values).  This is used within the dynamic programming
    algorithm.
    * ic - insertion cost
    * dc - deletion cost
    * sc - substitution cost
    * im - insertion match (score)
    * dm - deletion match (score)
    * sm - substitution match (score)
    """
    # pylint: disable=unused-argument
    best_action = None
    lowest_cost = float("inf")
    max_match = max(im, dm, sm)
    if max_match == sm and cost == 0:
        best_action = EQUAL
        lowest_cost = sm
    elif max_match == sm and cost == 1:
        best_action = REPLACE
        lowest_cost = sm
    elif max_match == im and ic < lowest_cost:
        best_action = INSERT
        lowest_cost = ic
    elif max_match == dm and dc < lowest_cost:
        best_action = DELETE
        lowest_cost = dc
    return best_action


class SequenceMatcher(object):
    """Similar to the :py:mod:`difflib` :py:class:`~difflib.SequenceMatcher`, but uses Levenshtein/edit
    distance.
    """

    def __init__(self, a=None, b=None, test=operator.eq,
                 action_function=lowest_cost_action):
        """Initialize the object with sequences a and b.  Optionally, one can
        specify a test function that is used to compare sequence elements.
        This defaults to the built in ``eq`` operator (i.e. :py:func:`operator.eq`).
        """
        if a is None:
            a = []
        if b is None:
            b = []
        self.seq1 = a
        self.seq2 = b
        self._reset_object()
        self.action_function = action_function
        self.test = test
        self.dist = None
        self._matches = None
        self.opcodes = None

    def set_seqs(self, a, b):
        """Specify two alternative sequences -- reset any cached values."""
        self.set_seq1(a)
        self.set_seq2(b)
        self._reset_object()

    def _reset_object(self):
        """Clear out the cached values for distance, matches, and opcodes."""
        self.opcodes = None
        self.dist = None
        self._matches = None

    def set_seq1(self, a):
        """Specify a new sequence for sequence 1, resetting cached values."""
        self._reset_object()
        self.seq1 = a

    def set_seq2(self, b):
        """Specify a new sequence for sequence 2, resetting cached values."""
        self._reset_object()
        self.seq2 = b

    def find_longest_match(self, alo, ahi, blo, bhi):
        """Not implemented!"""
        raise NotImplementedError()

    def get_matching_blocks(self):
        """Similar to :py:meth:`get_opcodes`, but returns only the opcodes that are
        equal and returns them in a somewhat different format
        (i.e. ``(i, j, n)`` )."""
        opcodes = self.get_opcodes()
        match_opcodes = filter(lambda x: x[0] == EQUAL, opcodes)
        return map(lambda opcode: [opcode[1], opcode[3], opcode[2] - opcode[1]],
                   match_opcodes)

    def get_opcodes(self):
        """Returns a list of opcodes.  Opcodes are the same as defined by
        :py:mod:`difflib`."""
        if not self.opcodes:
            d, m, opcodes = edit_distance_backpointer(self.seq1, self.seq2,
                                                      action_function=self.action_function,
                                                      test=self.test)
            if self.dist:
                assert d == self.dist
            if self._matches:
                assert m == self._matches
            self.dist = d
            self._matches = m
            self.opcodes = opcodes
        return self.opcodes

    def get_grouped_opcodes(self, n=None):
        """Not implemented!"""
        raise NotImplementedError()

    def ratio(self):
        """Ratio of matches to the average sequence length."""
        return 2.0 * self.matches() / (len(self.seq1) + len(self.seq2))

    def quick_ratio(self):
        """Same as :py:meth:`ratio`."""
        return self.ratio()

    def real_quick_ratio(self):
        """Same as :py:meth:`ratio`."""
        return self.ratio()

    def _compute_distance_fast(self):
        """Calls edit_distance, and asserts that if we already have values for
        matches and distance, that they match."""
        d, m = edit_distance(self.seq1, self.seq2,
                             action_function=self.action_function,
                             test=self.test)
        if self.dist:
            assert d == self.dist
        if self._matches:
            assert m == self._matches
        self.dist = d
        self._matches = m

    def distance(self):
        """Returns the edit distance of the two loaded sequences.  This should
        be a little faster than getting the same information from
        :py:meth:`get_opcodes`."""
        if not self.dist:
            self._compute_distance_fast()
        return self.dist

    def matches(self):
        """Returns the number of matches in the alignment of the two sequences.
        This should be a little faster than getting the same information from
        :py:meth:`get_opcodes`."""
        if not self._matches:
            self._compute_distance_fast()
        return self._matches


def edit_distance(seq1, seq2, action_function=lowest_cost_action, test=operator.eq):
    """Computes the edit distance between the two given sequences.
    This uses the relatively fast method that only constructs
    two columns of the 2d array for edits.  This function actually uses four columns
    because we track the number of matches too.
    """
    m = len(seq1)
    n = len(seq2)
    # Special, easy cases:
    if seq1 == seq2:
        return 0, n
    if m == 0:
        return n, 0
    if n == 0:
        return m, 0
    v0 = [0] * (n + 1)  # The two 'error' columns
    v1 = [0] * (n + 1)
    m0 = [0] * (n + 1)  # The two 'match' columns
    m1 = [0] * (n + 1)
    for i in range(1, n + 1):
        v0[i] = i
    for i in range(1, m + 1):
        v1[0] = i
        for j in range(1, n + 1):
            cost = 0 if test(seq1[i - 1], seq2[j - 1]) else 1
            # The costs
            ins_cost = v1[j - 1] + 1
            del_cost = v0[j] + 1
            sub_cost = v0[j - 1] + cost
            # Match counts
            ins_match = m1[j - 1]
            del_match = m0[j]
            sub_match = m0[j - 1] + int(not cost)

            action = action_function(ins_cost, del_cost, sub_cost, ins_match,
                                     del_match, sub_match, cost)

            if action in [EQUAL, REPLACE]:
                v1[j] = sub_cost
                m1[j] = sub_match
            elif action == INSERT:
                v1[j] = ins_cost
                m1[j] = ins_match
            elif action == DELETE:
                v1[j] = del_cost
                m1[j] = del_match
            else:
                raise Exception('Invalid dynamic programming option returned!')
                # Copy the columns over
        for i in range(0, n + 1):
            v0[i] = v1[i]
            m0[i] = m1[i]
    return v1[n], m1[n]


def edit_distance_backpointer(seq1, seq2, action_function=lowest_cost_action, test=operator.eq):
    """Similar to :py:func:`~edit_distance.edit_distance` except that this function keeps backpointers
    during the search.  This allows us to return the opcodes (i.e. the specific
    edits that were used to change from one string to another).  This function
    contructs the full 2d array (actually it contructs three of them: one
    for distances, one for matches, and one for backpointers)."""
    matches = 0
    # Create a 2d distance array
    m = len(seq1)
    n = len(seq2)
    # distances array:
    d = [[0 for x in range(n + 1)] for y in range(m + 1)]
    # backpointer array:
    bp = [[None for x in range(n + 1)] for y in range(m + 1)]
    # matches array:
    matches = [[0 for x in range(n + 1)] for y in range(m + 1)]
    # source prefixes can be transformed into empty string by
    # dropping all characters
    for i in range(1, m + 1):
        d[i][0] = i
        bp[i][0] = [DELETE, i - 1, i, 0, 0]
    # target prefixes can be reached from empty source prefix by inserting
    # every characters
    for j in range(1, n + 1):
        d[0][j] = j
        bp[0][j] = [INSERT, 0, 0, j - 1, j]
    # compute the edit distance...
    for i in range(1, m + 1):
        for j in range(1, n + 1):

            cost = 0 if test(seq1[i - 1], seq2[j - 1]) else 1
            # The costs of each action...
            ins_cost = d[i][j - 1] + 1  # insertion
            del_cost = d[i - 1][j] + 1  # deletion
            sub_cost = d[i - 1][j - 1] + cost  # substitution/match

            # The match scores of each action
            ins_match = matches[i][j - 1]
            del_match = matches[i - 1][j]
            sub_match = matches[i - 1][j - 1] + int(not cost)

            action = action_function(ins_cost, del_cost, sub_cost, ins_match,
                                     del_match, sub_match, cost)
            if action == EQUAL:
                d[i][j] = sub_cost
                matches[i][j] = sub_match
                bp[i][j] = [EQUAL, i - 1, i, j - 1, j]
            elif action == REPLACE:
                d[i][j] = sub_cost
                matches[i][j] = sub_match
                bp[i][j] = [REPLACE, i - 1, i, j - 1, j]
            elif action == INSERT:
                d[i][j] = ins_cost
                matches[i][j] = ins_match
                bp[i][j] = [INSERT, i - 1, i - 1, j - 1, j]
            elif action == DELETE:
                d[i][j] = del_cost
                matches[i][j] = del_match
                bp[i][j] = [DELETE, i - 1, i, j - 1, j - 1]
            else:
                raise Exception('Invalid dynamic programming action returned!')

    opcodes = get_opcodes_from_bp_table(bp)
    return d[m][n], matches[m][n], opcodes


def get_opcodes_from_bp_table(bp):
    """Given a 2d list structure, collect the opcodes from the best path."""
    x = len(bp) - 1
    y = len(bp[0]) - 1
    opcodes = []
    while x != 0 or y != 0:
        this_bp = bp[x][y]
        opcodes.append(this_bp)
        if this_bp[0] == EQUAL or this_bp[0] == REPLACE:
            x = x - 1
            y = y - 1
        elif this_bp[0] == INSERT:
            y = y - 1
        elif this_bp[0] == DELETE:
            x = x - 1
    opcodes.reverse()
    return opcodes


if __name__ == '__main__':
    main()
