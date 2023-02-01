################################################################################
# Build the database for GFF utils
#
# Author: Kobie Kirven
# Assmann and Bevilacqua Labs
# The Penn State University
################################################################################

import argparse
import gffutils
import sys
import os

parser = argparse.ArgumentParser(description="Build the database for gffutils")
parser.add_argument("--gtf", dest="gtf", help="GTF File")
parser.add_argument("--o", dest="out", help="output_directory")
args = parser.parse_args()

# Check to make sure the the input file exists
if not os.path.exists(args.gtf):
    print("GTF file does not exist")
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
    print("Error: Could not create database. Please check your GTF file.")
    sys.exit(1)
