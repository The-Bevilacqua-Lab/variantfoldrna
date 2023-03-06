################################################################################
# Build the database for gffutils
#
# Author: Kobie Kirven
# Assmann and Bevilacqua Labs
# The Penn State University
################################################################################

# --- Imports ---#
import argparse
import gffutils
import sys
import os
from gzip import open as gzopen


# --- Functions ---#
def is_gzipped(filename):
    """
    Check to make sure the file is gzipped
    """
    with open(filename, "rb") as f:
        magic_number = f.read(2)
        return magic_number == b"\x1f\x8b"


def is_gff_gtf_file(filename, gzip=False):
    """
    Check to make sure the file is a GFF/GTF file
    """
    if not gzip:
        with open(filename) as f:
            first_line = f.readline().strip()
            return first_line.startswith("##gff-version") or first_line.startswith("#")
    else:
        with gzopen(filename, "rb") as f:
            first_line = f.readline().strip().decode("utf-8")
            return first_line.startswith("##gff-version") or first_line.startswith("#")


def print_red(text):
    """
    Print in red
    """
    print("\033[91m {}\033[00m".format(text))


# --- Main ---#
if __name__ == "__main__":
    # Parse the arguments
    parser = argparse.ArgumentParser(description="Build the database for gffutils")
    parser.add_argument("--gtf", dest="gtf", help="GTF File")
    parser.add_argument("--o", dest="out", help="output_directory")
    args = parser.parse_args()

    # Check to make sure the the input file exists
    if not os.path.exists(args.gtf):
        print("GTF file does not exist")
        sys.exit(1)

    # Check to make sure the the input file exists
    if not os.path.exists(args.gtf):
        print_red("GTF file does not exist")
        sys.exit(1)

    # Check to make sure the file is a GFF/GTF file
    if not is_gff_gtf_file(args.gtf, gzip=is_gzipped(args.gtf)):
        print_red("Error: File does not appear to be a GFF/GTF file")
        sys.exit(1)

    # Create the database
    try:
        db = gffutils.create_db(
            args.gtf,
            dbfn=args.out,
            force=True,
            merge_strategy="merge",
            disable_infer_transcripts=True,
            disable_infer_genes=True,
        )
    except:
        print_red("Error: Could not create database! Please check your GTF file.")
        sys.exit(1)
