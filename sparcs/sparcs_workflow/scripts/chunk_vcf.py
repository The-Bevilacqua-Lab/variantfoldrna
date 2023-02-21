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
if args.input.endswith(".gz"):
    vcf_gz = True
else:
    vcf_gz = False

# Make a directory to store the VCF chunks
if not os.path.exists(f"{args.dir}/vcf_chunks/"):
    try:
        os.system(f"mkdir -p {args.dir}/vcf_chunks/")
    except:
        prRed("Error: Can not create directory to hold VCF chunks")
        sys.exit(1)

def get_vcf_len(file_name, gzip_file=False):
    """
    Get the number of lines in the VCF file
    """
    total = 0

    if gzip_file:
        print(file_name)
        fn = gzip.open(file_name, 'rb')
    else:
        fn = open(file_name)
    for line in fn:
        if line.startswith("#".encode()):
            continue
        else:
            total += 1
    return total

# Get the number of lines in the VCF file
vcf_len = get_vcf_len(args.input, gzip_file=vcf_gz)

# Check to see if we are splitting the VCF file into more chunks than there are lines
if int(args.chunk) == 1:
    chunk_len = vcf_len
else:
    # Get the length of the chunks
    chunk_len = vcf_len // (int(args.chunk) - 1)

# Split the VCF file up into tiny files

# If the VCF file is gzipped, we need to open it differently
if vcf_gz:
    in_file = gzip.open(args.input, "rb")
else:
    in_file = open(args.input, "r")

header_one = in_file.readline()
for i in range(1, int(args.chunk)):
    fn = gzip.open(f"{args.dir}/vcf_chunks/vcf_no_header_{i}.vcf.gz", "wb")
    with gzip.open(args.header, "rb") as header:
        for line in header:
            fn.write(line)
    fn.write(header_one)
    for g in range(chunk_len):
        fn.write(in_file.readline())
    fn.close()

# Write what's left to the last file
fn = gzip.open(f"{args.dir}/vcf_chunks/vcf_no_header_{int(args.chunk)}.vcf.gz", "wb")
with gzip.open(args.header, "rb") as header:
    for line in header:
        fn.write(line)
fn.write(header_one)

for line in in_file:
    fn.write(line)
fn.close()
