################################################################################
# Test the get_read_data.py script
#
# Author: Kobie Kirven
# Assmann and Bevilacqua Labs
# The Penn State University
################################################################################

# -- Imports -- #
import os
import sys
import gzip
import tempfile
import subprocess

# Add the path to the build_gffutils.py to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "sparcs", "sparcs_workflow", "scripts"))

# Import the functions from the build_gffutils.py script
from get_read_data import compelement_dna, five_prime_test, three_prime_test

def test_complement_dna():
    assert compelement_dna("A") == "T"
    assert compelement_dna("T") == "A"
    assert compelement_dna("C") == "G"
    assert compelement_dna("G") == "C"
    assert compelement_dna("N") == "N"
    assert compelement_dna("a") == "T"
    assert compelement_dna("t") == "A"
    assert compelement_dna("c") == "G"
    assert compelement_dna("g") == "C"
    assert compelement_dna("n") == "N"
    assert compelement_dna("ATCG") == "TAGC"

def test_five_prime():
    assert five_prime_test(5,1,1) == True
    assert five_prime_test(5,1,4) == True
    assert five_prime_test(5,1,5) == False

def test_three_prime():
    assert three_prime_test(5,10,5) == True
    assert three_prime_test(5,10,6) == False

def test_main():
    path = os.path.join(os.path.dirname(__file__), "..", "..", "sparcs", "sparcs_workflow", "scripts", "get_read_data.py")
    data_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "get_read_data")
    command = subprocess.run(["python3", path, "--vcf", f"{data_path}/test_coords.txt", "--database", f"{data_path}/test.db", 
    "--ref-genome", f"{data_path}/chr1.fa", "--o", "test_output.txt", "--flank", "5"])
    assert command.returncode == 0
    