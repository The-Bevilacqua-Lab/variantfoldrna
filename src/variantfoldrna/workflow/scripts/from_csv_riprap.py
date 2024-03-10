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


def run_riprap(sequence, mutation, path, temp, minwindow, tool, win_type=0):
    """
    Run RipRap on the sequence.
    """
    if "N" in sequence.upper():
        return "Error"

    # Make the input file:
    fn, name = make_temp_riprap_input(sequence, mutation)
    name = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(6)
    )

    # Run RipRap:
    riprap = subprocess.run(
        [
            "python3",
            "{0}/riprap.py".format(path),
            "--i",
            fn,
            "--o",
            name,
            "--foldtype",
            str(tool),
            "-T",
            str(temp),
            "-w",
            str(minwindow),
            "-f",
            str(win_type),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Read the output:
    with open("{0}_riprap_score.tab".format(name)) as f:
        lines = f.readlines()

    # Remove the temporary file:
    os.remove("{0}_riprap_score.tab".format(name))

    # Return the score:
    try:
        score = lines[1].split(",")[1]
        return score
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
    parser.add_argument(
        "--windowtype", dest="windowtype", help="Window Type", default=0
    )
    parser.add_argument("--tool", dest="tool", help="Tool", default="RNAfold")
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
            line = line.split(",")

            # Check to make sure we don't have any indels
            if not len(line[1]) == 1 or not len(line[2]) == 1:
                continue

            # Change the reference and alternative alleles
            if line[1] == "T":
                line[1] = "U"
            if line[2] == "T":
                line[2] = "U"
            flank = int(line[4])
            # Get the sequence and the mutation
            seq = line[3]
            mutation = f"{line[1]}{flank + 1}{line[2]}"

            # Get the tool number:
            if args.tool == "RNAfold":
                number = 1
            if args.tool == "RNAstructure":
                number = 2

            # Get the path:
            path = os.path.dirname(os.path.realpath(__file__))

            # Run RipRap:
            score = run_riprap(
                seq, mutation, path, args.temp, args.minwindow, number, args.windowtype
            )

            # Write the output:
            if score == "NA":
                error.write("\t".join(line) + "\n")
            else:
                out.write("\t".join(line).strip("\n") + "\t" + str(score) + "\n")