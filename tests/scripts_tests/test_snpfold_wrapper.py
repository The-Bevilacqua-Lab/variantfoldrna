##############################################################################
# Testing the functionality of the snpfold_wrapper.py script
# 
##############################################################################

# -- Imports --#
import subprocess 
import os
import sys


# Add the path to the build_gffutils.py to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "sparcs", "sparcs_workflow", "scripts"))

data_path = os.path.join(os.path.dirname(__file__), "..", "..", "sparcs")


# Import the functions from the snpfold_wrapper.py script
from snpfold_wrapper import transcribe_rna, change_nuc, run_snpfold

def test_transcribe_rna():
    assert transcribe_rna("ATGC") == "AUGC"

def test_change_nuc():
    assert change_nuc("A") == "U"
    assert change_nuc("T") == "A"
    assert change_nuc("G") == "C"
    assert change_nuc("C") == "G"

def test_run_snpfold():
    # Test the normal case
    seq = "AGCCGGAAGGAGAGCUCUACUACUA"
    mut = "A8G"
    temp = "37"
    score = run_snpfold(seq, data_path, temp, mut)
    assert type(float(score)) == float

    # Test changing the temperature
    temp = "38"
    score = run_snpfold(seq, data_path, temp, mut)
    assert type(float(score)) == float

    # Test the error handling -- "N" in the sequence
    seq = "AGCCGGAAGGANAGCUCUANUACUA"
    score = run_snpfold(seq, data_path, temp, mut)
    assert score == "Error"
