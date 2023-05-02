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

if __name__ == "__main__":
    # ----- Parse arguments ----#
    parser = argparse.ArgumentParser(description="Plot results")
    parser.add_argument("--i", dest="in_file", help="Input RiboSNitch Results File")
    parser.add_argument("--t", dest="tool", help="Tool used to predict riboSNitches")
    parser.add_argument("--o", dest="out", help="Output folder")
    args = parser.parse_args()

    # Read in the input data
    data = pd.read_csv(args.in_file, sep="\t")

    # Plot the scores
    plt.style.use("grayscale")
    plt.hist(data["Score"], color="royalblue")

    # Check to see which tool was used and update the plot accordingly
    if args.tool.upper() == "SNPFOLD":
        plt.title("SNPfold Scores")
        plt.xlabel("SNPfold Score")
        plt.ylabel("# of SNPs")
        plt.savefig(f"{args.out}", bbox_inches="tight", dpi=200)

    elif args.tool.upper() == "RIPRAP":
        plt.title("Riprap Scores")
        plt.xlabel("Riprap Score")
        plt.ylabel("# of SNPs")
        plt.savefig(f"{args.out}", bbox_inches="tight", dpi=200)

    elif args.tool.upper() == "RNASNP":
        plt.title("RNAsnp:p-value")
        plt.xlabel("RNAsnp:p-value")
        plt.ylabel("# of SNPs")
        plt.savefig(f"{args.out}", bbox_inches="tight", dpi=200)