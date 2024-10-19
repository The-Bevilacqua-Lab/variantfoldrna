################################################################################
# Wrapper for the remuRNA tool
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
import sys

output = subprocess.check_output("echo $CONDA_DEFAULT_ENV", shell=True, encoding='utf-8')

# Define the relative path to your target directory inside the conda environment
target_directory = output.strip() +  "/lib/data"

os.chdir(target_directory)

# -- Functions --#
def make_temp_remurna_inputs(sequence, mutation):
    """
    Create a temporary input file for RNAsnp
    """
    fn = tempfile.NamedTemporaryFile(delete=False)
    name = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(6)
    )
    fn.close()

    # Create a file to hold the input sequence
    with open(f"{fn.name}.fa", "w") as seq:
        seq.write(f">test\n{sequence}*{mutation}")

    return f"{fn.name}.fa"


def run_remurna(sequence, mutation, temperature, target_directory):
    """
    Run RNAsnp on the sequence
    """
    if "N" in sequence.upper():
        return "Error"

    # Make the input file:
    seq = make_temp_remurna_inputs(sequence, mutation)

    # Run RNAsnp

    remurna = subprocess.run(["remuRNA",
            seq,
            f"--tmin={temperature}",
            f"--tmax={temperature}",
        ]
        ,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Remove the temporary files
    subprocess.run(["rm", seq])

    # Read the output
    try:
        entropy = remurna.stdout.decode("utf-8").split("\n")[1].split("\t")[4]
    except:
        return "Error"

    return entropy


# -- Main --#
if __name__ == "__main__":
    # Parse the arguments:
    parser = argparse.ArgumentParser(description="RNAsnp Wrapper")
    parser.add_argument("--i", dest="in_file", help="Input File")
    parser.add_argument("--o", dest="output", help="Output")
    parser.add_argument("--flank", dest="flank", help="Flanking length")
    parser.add_argument("--temp", dest="temp", help="Temperature", default=37.0)
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
            score = run_remurna(seq, mutation, args.temp, target_directory)

            # Write the output:
            if score == "NA":
                error.write("\t".join(line) + "\n")
            else:
                out.write("\t".join(line).strip("\n") + "\t" + str(score) + "\n")
