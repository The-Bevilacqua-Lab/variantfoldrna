################################################################################
# Wrapper for RipRap prediction tool
#
# Author: Kobie Kirven
#
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
################################################################################

# Imports
import argparse
import numpy as np
import subprocess
import tempfile
import os
import string
import random

# Get the location of this file:
location = os.getcwd()

# Get the path up to the SPARCS directory:
path = []
for ele in location.split("/"):
    if ele == "SPARCS":
        path.append(ele)
        break
    else:
        path.append(ele)

# Convert the path to a string:
path = "/".join(path)


def make_temp_riprap_input(sequence, mutation):
    """
    Create a temporary input file for RipRap
    """
    fn = tempfile.NamedTemporaryFile(delete=False)
    name = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(6)
    )
    fn.write(b">.sq" + name.encode("utf-8") + b"\n")
    fn.write(sequence.encode("utf-8"))
    return fn.name, name


parser = argparse.ArgumentParser(description="Determine RiboSNitches")
parser.add_argument("--i", dest="in_file", help="Input File")
parser.add_argument("--o", dest="output", help="Output")
parser.add_argument("--flank", dest="flank", help="Flanking length")
parser.add_argument("--temp", dest="temp", help="Temperature")
args = parser.parse_args()


