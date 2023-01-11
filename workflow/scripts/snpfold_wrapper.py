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

parser = argparse.ArgumentParser(description="Determine RiboSNitches")
parser.add_argument("--i", dest="in_file", help="Input File")
parser.add_argument("--o", dest="output", help="Output")
parser.add_argument("--flank", dest="flank", help="Flanking length")

parser.add_argument("--temp", dest="temp", help="Temp")


def transcribe_rna(seq):
    return seq.replace("T", "U")


def change_nuc(nuc):
    nuc_dict = {"A": "U", "T": "A", "G": "C", "C": "G"}
    return nuc_dict[nuc]


args = parser.parse_args()

outfile = open(args.output, "w")
error = open(args.output.strip(".txt") + "_error.txt", "w")
ids, seqs = [], []

with open(args.in_file) as fn:
    for line in fn:
        if not line.startswith("#"):
            line = line.split("\t")

            if not len(line[3]) == 1 or not len(line[4]) == 1:
                continue

            # Change the reference and alternative alleles
            if line[2] == "T":
                line[2] = "U"
            if line[3] == "T":
                line[3] = "U"

            seq = str(line[5]) + str(line[3]) + str(line[6])

            # Run the riboSNitch analysis
            results = os.popen(
                "python3 "
                + path
                + "/workflow/scripts/calculate_pearson.py -T "
                + args.temp
                + " -seq "
                + transcribe_rna(seq)
                + "  -mut "
                + line[3]
                + (str(int(args.flank) + 1))
                + line[4]
            ).read()

            try:
                corr = results.split("\n")[0]
                outfile.write("\t".join(line).strip("\n") + "\t" + corr + "\n")
            except:
                error.write("\t".join(line) + "\n")
fn.close()
error.close()
