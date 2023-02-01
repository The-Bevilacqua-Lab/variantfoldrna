################################################################################
# Break up VCF files into smaller ones so that they are easier to work with
#
# Author: Kobie Kirven
# Assmann and Bevilacqua Labs
# The Penn State University
################################################################################

from email import header
import subprocess
import argparse
import os

#######################
#  --  Functions --   #
#######################
parser = argparse.ArgumentParser(description="Break up VCF file")
parser.add_argument("--input", dest="input", help="input file")
parser.add_argument("--dir", dest="dir", help="working directory")
parser.add_argument(
    "--chunk-total", dest="chunk", help="The number of files to chop the input into"
)
args = parser.parse_args()

# Make a directory to store the VCF chunks
os.system(f"mkdir -p {args.dir}/extracted_seqs_chunks/")


def get_file_len(file_name):
    """
    Get the number of lines in the file
    """
    total = 0
    with open(file_name) as fn:
        for line in fn:
            total += 1
    return total


# Get the number of lines in the VCF file
file_len = get_file_len(args.input)

if int(args.chunk) == 1:
    chunk_len = file_len
else:
    # Get the length of the chunks
    chunk_len = file_len // (int(args.chunk) - 1)

# Split the VCF file up into tiny files
in_file = open(args.input, "r")
for i in range(1, int(args.chunk)):
    fn = open(f"{args.dir}/extracted_seqs_chunks/extracted_flank_snp_{i}.txt", "w")
    for g in range(chunk_len):
        fn.write(in_file.readline())
    fn.close()
fn = open(
    f"{args.dir}/extracted_seqs_chunks/extracted_flank_snp_{int(args.chunk)}.txt", "w"
)
for line in in_file:
    fn.write(line)
fn.close()
