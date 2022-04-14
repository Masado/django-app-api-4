#!/usr/bin/env python3

from ete3 import NCBITaxa

ncbi = NCBITaxa()

name2taxid = ncbi.get_name_translator(["Gallus gallus"])
tax_value = name2taxid["Gallus gallus"]
species_id = tax_value[0]
print("species_id", species_id)
print("finished name2taxid")
