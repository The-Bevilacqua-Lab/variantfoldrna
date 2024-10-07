################################################################################
# Wrapper for RNAsnp tool
#
# Author: Kobie Kirven
#
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
################################################################################

# -- Imports --#
import argparse
import subprocess
import tempfile
import os
import string
import random


# -- Functions --#
def make_temp_rnasnp_inputs(sequence, mutation):
    """
    Create a temporary input file for RNAsnp
    """
    fn = tempfile.NamedTemporaryFile(delete=False)
    name = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(6)
    )
    fn.close()

    # Create a file to hold the input sequence
    with open(f"{fn.name}.seq", "w") as seq:
        seq.write(sequence)

    # Create a file to hold the mutation
    with open(f"{fn.name}.mut", "w") as mut:
        mut.write(mutation)

    return f"{fn.name}.seq", f"{fn.name}.mut"


def run_rnasnp(sequence, mutation, flank, kind):
    """
    Run RNAsnp on the sequence
    """
    if "N" in sequence.upper():
        return "Error"

    # Make the input file:
    seq, mut = make_temp_rnasnp_inputs(sequence, mutation)

    # Run RNAsnp
    rnasnp = subprocess.run(
        ["RNAsnp", "-f", seq, "-s", mut, "-w", str(int(flank)*2)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Remove the temporary files
    os.remove(seq)
    os.remove(mut)

    # Read the output
    try:
        dist = rnasnp.stdout.decode("utf-8").split("\n")[1].split("\t")[5]
        p_value = rnasnp.stdout.decode("utf-8").split("\n")[1].split("\t")[6]

    except:
        return "Error"

    if kind == "dist":
        return dist
    else:
        return p_value


# -- Main --#
if __name__ == "__main__":
    # Parse the arguments:
    parser = argparse.ArgumentParser(description="RNAsnp Wrapper")
    parser.add_argument("--i", dest="in_file", help="Input File")
    parser.add_argument("--o", dest="output", help="Output")
    parser.add_argument("--flank", dest="flank", help="Flanking length")
    parser.add_argument("--kind", dest="kind", help="Dist or p_value")
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
            mutation = f"{line[1]}{flank}{line[2]}"

            # Get the path:
            path = os.path.dirname(os.path.realpath(__file__))

            # Run RipRap:
            score = run_rnasnp(seq.replace("T","U"), mutation, args.flank, args.kind)

            # Write the output:
            if score == "NA" or "Reference allele" in score:
                error.write("\t".join(line) + "\n")
            else:
                out.write("\t".join(line).strip("\n") + "\t" + str(score) + "\n")
