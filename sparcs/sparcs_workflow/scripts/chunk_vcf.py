################################################################################
# Break up VCF files into smaller ones so that they are easier to work with
#
# Author: Kobie Kirven
# Assmann and Bevilacqua Labs
# The Penn State University
################################################################################

import argparse
import os
import gzip 
import sys

#######################
#  --  Functions --   #
#######################
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))
def prCyan(skk): print("\033[96m {}\033[00m" .format(skk))
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))

parser = argparse.ArgumentParser(description="Break up VCF file")
parser.add_argument("--input", dest="input", help="input file")
parser.add_argument("--dir", dest="dir", help="working directory")
parser.add_argument("--vcf-header", dest="header", help="Header")
parser.add_argument(
    "--chunk-total", dest="chunk", help="The number of files to chop the input into"
)
args = parser.parse_args()

# Check to see if we are dealing with a gzipped VCF file or not
if args.input.ends

# Make a directory to store the VCF chunks
if not os.path.exists(f"{args.dir}/vcf_chunks/"):
    try:
        os.system(f"mkdir -p {args.dir}/vcf_chunks/")
    except:
        prRed("Error: Can not create directory to hold VCF chunks")
        sys.exit(1)

def get_vcf_len(file_name, gzip=False):
    """
    Get the number of lines in the VCF file
    """
    total = 0
    if gzip:
        fn = gzip.open(file_name, 'rb')
    else:
        fn = open(file_name)
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
