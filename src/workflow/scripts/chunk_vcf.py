################################################################################
# Break up VCF files into smaller ones so that they are easier to work with
#
# Author: Kobie Kirven
# Assmann and Bevilacqua Labs
# The Penn State University
################################################################################

import subprocess
import argparse
import os
import copy

#######################
#  --  Functions --   #
#######################
parser = argparse.ArgumentParser(description="Break up VCF file")
parser.add_argument("--input", dest="input", help="input file")
parser.add_argument("--dir", dest="dir", help="working directory")
parser.add_argument("--vcf-header", dest="header", help="Header")
parser.add_argument(
    "--chunk-total", dest="chunk", help="The number of files to chop the input into"
)
args = parser.parse_args()

# Make a directory to store the VCF chunks
if not os.path.exists(f"{args.dir}/vcf_chunks/"):
    os.system(f"mkdir -p {args.dir}/vcf_chunks/")


def get_vcf_len(file_name):
    """
    Get the number of lines in the VCF file
    """
    total = 0
    with open(file_name) as fn:
        for line in fn:
            if line.startswith("#"):
                continue
            else:
                total += 1
    return total


# Get the number of lines in the VCF file
vcf_len = get_vcf_len(args.input)

if int(args.chunk) == 1:
    chunk_len = vcf_len
else:
    # Get the length of the chunks
    chunk_len = vcf_len // (int(args.chunk) - 1)

# Split the VCF file up into tiny files
in_file = open(args.input, "r")
header_one = str(in_file.readline())
for i in range(1, int(args.chunk)):
    fn = open(f"{args.dir}/vcf_chunks/vcf_no_header_{i}.vcf", "w")
    with open(args.header, "r") as header:
        for line in header:
            fn.write(line)
    fn.write(header_one)
    for g in range(chunk_len):
        fn.write(in_file.readline())
    fn.close()

# Write what's left to the last file
fn = open(f"{args.dir}/vcf_chunks/vcf_no_header_{int(args.chunk)}.vcf", "w")
with open(args.header, "r") as header:
    for line in header:
        fn.write(line)
fn.write(header_one)
for line in in_file:
    fn.write(line)
fn.close()
