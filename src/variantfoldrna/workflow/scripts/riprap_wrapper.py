################################################################################
# Wrapper for RipRap prediction tool
#
# Author: Kobie Kirven
#
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
################################################################################

# -- Imports --#
import argparse
import numpy as np
import subprocess
import tempfile
import os
import string
import random


# -- Functions --#
def make_temp_riprap_input(sequence, mutation):
    """
    Create a temporary input file for RipRap.
    We will use random integers and letters to name the sequence.
    """
    fn = tempfile.NamedTemporaryFile(delete=False)
    name = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(6)
    )

    fn.write(("{0}\t{1}\t{2}\n".format(name, sequence, mutation).encode("utf-8")))
    return fn.name, name


def run_riprap(seq, path, temp, mutation, minW=3):
    """
    Run RipRap on the sequence.
    """
    results = subprocess.run(
        [f"{path}/../bin/riprap", "-T", str(temp), "-seq", str(seq), "-mut", str(mutation), "-minW", str(minW)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )   
    try:
        return results.stdout.decode("utf-8")
    except:
        return "Error"


# -- Main --#
if __name__ == "__main__":
    # Parse the arguments:
    parser = argparse.ArgumentParser(description="Determine RiboSNitches")
    parser.add_argument("--i", dest="in_file", help="Input File")
    parser.add_argument("--o", dest="output", help="Output")
    parser.add_argument("--flank", dest="flank", help="Flanking length")
    parser.add_argument("--temp", dest="temp", help="Temperature", default=37.0)
    parser.add_argument(
        "--minwindow", dest="minwindow", help="Minimum Window", default=3
    )
    args = parser.parse_args()

    # Open the input file
    fn = open(args.in_file)
    lines = fn.readlines()

    # Open the output files and the error
    out = open(args.output, "w")
    error = open(args.output[:-4] + "_error.txt", "w")

    # Loop through the input file and perform the riboSNitch prediction:
    for line in lines:
        # Skip the header:
        if not line.startswith("#"):
            line = line.split("\t")

            # Check to make sure we don't have any indels
            if not len(line[3]) == 1 or not len(line[4]) == 1:
                continue

            # Change the reference and alternative alleles
            if line[3] == "T":
                line[3] = "U"
            if line[4] == "T":
                line[4] = "U"

            # Get the sequence and the mutation
            seq = str(line[5]) + str(line[3]) + str(line[6])
            mutation = f"{line[3]}{int(args.flank) + 1}{line[4]}"

            # Get the path:
            path = os.path.dirname(os.path.realpath(__file__))

            # Run RipRap:
            score = run_riprap(
                seq, path, float(args.temp), mutation, args.minwindow
            )

            # Write the output:
            if score == "NA":
                error.write("\t".join(line) + "\n")
            else:
                out.write("\t".join(line).strip("\n") + "\t" + str(score))
