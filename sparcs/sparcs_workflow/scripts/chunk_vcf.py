################################################################################
# Break up VCF files into smaller ones so that they are easier to work with
#
# Author: Kobie Kirven
# Assmann and Bevilacqua Labs
# The Penn State University
################################################################################

# -- Imports --   #
import argparse
import os
import gzip 
import sys
import subprocess


#  --  Functions --   #
def prGreen(skk): 
    print("\033[92m {}\033[00m" .format(skk))

def prCyan(skk): 
    print("\033[96m {}\033[00m" .format(skk))

def prYellow(skk): 
    print("\033[93m {}\033[00m" .format(skk))

def prRed(skk): 
    print("\033[91m {}\033[00m" .format(skk))

def get_vcf_len(file_name, gzip_file=False):
    """
    Get the number of lines in the VCF file
    """
    total = 0
    if gzip_file:
        fn = gzip.open(file_name, 'rb')
        for line in fn:
            if line.startswith("#".encode()):
                continue
            else:
                total += 1
        return total
    else:
        fn = open(file_name)
        for line in fn:
            if line.startswith("#"):
                continue
            else:
                total += 1
        return total

def is_gzipped(file_name):
    """
    Check to see if a file is gzipped or not
    """
    with open(file_name, "rb") as f:
        return f.read(2) == b"\x1f\x8b"

def create_output_dir(dir_name):
    # Make a directory to store the VCF chunks
    if not os.path.exists(f"{dir_name}/vcf_chunks/"):
        try:
            os.system(f"mkdir -p {dir_name}/vcf_chunks/")
        except:
            prRed("Error: Can not create directory to hold VCF chunks")
            sys.exit(1)

def split_file_by_line(filename, n):
    gzip_file = is_gzipped(filename)
    if gzip_file:
        f = gzip.open(filename, 'rb')
    else:
        f = open(filename)
        
    f.seek(1)
    chunk_size = sum(1 for line in f) // n
    f.seek(1)
    remainder = sum(1 for line in f) % n
    f.seek(1)
    header = f.readline()
    start = 0
    for i in range(n):
        chunk = [f"#{header.decode()}"]
        if gzip_file:
            for j in range(chunk_size + (i < remainder)):
                chunk.append(f.readline().decode())
            yield chunk
        else:
            for j in range(chunk_size + (i < remainder)):
                chunk.append(f.readline())
            yield chunk

def chunk_vcf(vcf_file, chunks, prefix, header):
    header = open(header, "r").readlines()
    for i, chunk in enumerate(split_file_by_line(vcf_file, chunks)):
        with open(f"{prefix}_{i}.vcf", "w") as f:
            for line in header:
                f.write(line)
            for line in chunk:
                f.write(line)

# -- main --   #
if __name__ == "__main__":

    # Parse the arguments
    parser = argparse.ArgumentParser(description="Break up VCF file")
    parser.add_argument("--input", dest="input", help="input file")
    parser.add_argument("--dir", dest="dir", help="working directory")
    parser.add_argument("--vcf-header", dest="header", help="Header")
    parser.add_argument(
        "--chunk-total", dest="chunk", help="The number of files to chop the input into"
    )
    args = parser.parse_args()


    # Check to see if the input file is gzipped or not
    












# # Read in the first line of the VCF file which is the column header
# header_one = in_file.readline()
# for i in range(1, int(args.chunk)):
#     fn = gzip.open(f"{args.dir}/vcf_chunks/vcf_no_header_{i}.vcf.gz", "wb")

#     # Write the header to the file
#     with gzip.open(args.header, "rb") as header:
#         for line in header:
#             fn.write(line)

#     # Add the column header to the file
#     fn.write(header_one)

#     # Write the VCF lines to the file
#     for g in range(chunk_len):
#         fn.write(in_file.readline())
#     fn.close()

# # Write what's left to the last file
# fn = gzip.open(f"{args.dir}/vcf_chunks/vcf_no_header_{int(args.chunk)}.vcf.gz", "wb")

# # Write the header to the file
# with gzip.open(args.header, "rb") as header:
#     for line in header:
#         fn.write(line)
# fn.write(header_one)

# # Write the VCF lines to the file
# for line in in_file:
#     fn.write(line)
# fn.close()
