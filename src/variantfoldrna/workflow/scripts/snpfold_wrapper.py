################################################################################
# Wrapper for SNPfold prediction tool
#
# Author: Kobie Kirven
#
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
################################################################################

# Imports
import argparse
import os
import subprocess


# -- Functions -- #
def transcribe_rna(seq):
    """
    Convert the DNA sequence to RNA
    """
    return seq.replace("T", "U")


def change_nuc(nuc):
    """
    Complement nucleotides
    """
    nuc_dict = {"A": "U", "T": "A", "G": "C", "C": "G"}
    return nuc_dict[nuc]


def run_snpfold(seq, path, temp, mutation):
    """
    Run SNPfold on the sequence.
    """
    results = subprocess.run(
        [f"{path}/../bin/snpfold", "-T", temp, "-seq", seq, "-mut", mutation],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )   
    try:
        return results.stdout.decode("utf-8")
    except:
        return "Error"


if __name__ == "__main__":

    # Get the path to the sparcs directory
    path = os.path.dirname(os.path.realpath(__file__))
    # path = "../bin"
    # Parse the arguments
    parser = argparse.ArgumentParser(description="Determine RiboSNitches")
    parser.add_argument("--i", dest="in_file", help="Input File")
    parser.add_argument("--o", dest="output", help="Output")
    parser.add_argument("--flank", dest="flank", help="Flanking length")
    parser.add_argument("--temp", dest="temp", help="Temp")
    args = parser.parse_args()

    # Open the output files
    outfile = open(args.output, "w")
    error = open(args.output[:-4] + "_error.txt", "w")

    ids, seqs = [], []
    with open(args.in_file) as fn:
        for line in fn:

            # Skip the header
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

                # Run snpfold
                results = run_snpfold(transcribe_rna(seq), path, args.temp, mutation)

                # Write the results to the output file
                try:
                    previous = "\t".join(line).strip("\n")
                    results = '\t'.join(results.split(","))
                    outfile.write(f"{previous}\t{results}\n")
                except:
                    error.write("\t".join(line) + "\n")

    # Close the output and error files
    fn.close()
    error.close()
