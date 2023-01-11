#!/usr/bin/env python3
################################################################################
# Plot the results from the pipeline
#
# Author: Kobie Kirven
################################################################################

# Goal: Get a file with the reference sequence and the sequence with the
# alternative allele.


# ----- Import modules ----#
import argparse
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description="Plot results")
parser.add_argument("--i", dest="in_file", help="Input RiboSNitch Results File")
parser.add_argument("--o", dest="out", help="Output folder")

args = parser.parse_args()


plt.style.use("grayscale")
data = pd.read_csv(args.in_file, sep="\t", header=None)

plt.hist(data.iloc[:, 11], color="royalblue")
plt.xlabel("SNPfold Score")
plt.ylabel("# of SNVs")
plt.savefig(f"{args.out}", bbox_inches="tight", dpi=200)
