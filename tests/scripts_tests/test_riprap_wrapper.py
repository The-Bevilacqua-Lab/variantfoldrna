##############################################################################
# Testing the functionality of the riprap_wrapper.py script
# 
##############################################################################

# -- Imports --#
import subprocess 
import os
import sys


# Add the path to the build_gffutils.py to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "sparcs", "sparcs_workflow", "scripts"))

data_path = os.path.join(os.path.dirname(__file__), "..", "..", "sparcs")

# Import the functions from the build_gffutils.py script
from riprap_wrapper import make_temp_riprap_input, run_riprap

def test_make_temp_riprap_input():
    name, title = make_temp_riprap_input("AGCCGGUAGUGGUAGGUAG", "A8G")
    assert os.path.exists(name) == True
    assert open(name).read() == f"{title}\tAGCCGGUAGUGGUAGGUAG\tA8G\n"
    os.remove(name)

def test_run_riprap():
    score = run_riprap("AGCCGGAAGGAGAGCUCUACUACUA", "A8G", data_path, 37,3, 1)
    assert type(float(score)) == float

    score = run_riprap("AGCCGGAAGGANAGCUCUANUACUA", "A8G", data_path, 37,3, 1)
    assert score == "Error"

    score = run_riprap("AGCCGGAAGGAGAGCUCUACUACUA", "A8G", data_path, 37,3, 2)
    assert type(float(score)) == float

    score = run_riprap("AGCCGGAAGGANAGCUCUANUACUA", "A8G", data_path, 37,3, 2)
    assert score == "Error"