##############################################################################
# Remove any duplicate lines from a file.
#
# Author: Kobie Kirven
# Assmann and Bevilacqua Labs
# The Penn State University
##############################################################################

# -- Imports --#
import argparse
import pandas as pd

# -- Main -- #
if __name__ == "__main__":

    # Parse the arguments
    parser = argparse.ArgumentParser(description="Break up VCF file")
    parser.add_argument("-i", dest="input", help="input file")
    parser.add_argument("-o", dest="output", help="output file")
    args = parser.parse_args()

    # Read in the file
    data = pd.read_csv(args.input, header=None, sep="\t")

    # Remove duplicates
    data = data.drop_duplicates()

    # Write the output
    data.to_csv(args.output, sep="\t", index=False, header=False)
