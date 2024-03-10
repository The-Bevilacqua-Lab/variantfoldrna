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
    """
    Print in green
    """
    print("\033[92m {}\033[00m".format(skk))


def prCyan(skk):
    """
    Print in cyan
    """
    print("\033[96m {}\033[00m".format(skk))


def prYellow(skk):
    """
    Print in yellow
    """
    print("\033[93m {}\033[00m".format(skk))


def prRed(skk):
    """
    Print in red
    """
    print("\033[91m {}\033[00m".format(skk))


def get_vcf_len(file_name, gzip_file=False):
    """
    Get the number of lines in the VCF file
    """
    total = 0
    if gzip_file:
        fn = gzip.open(file_name, "rb")
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


def is_gzipped(file_path):
    with open(file_path, "rb") as f:
        # Check the first two bytes for the GZIP magic number
        lines = f.read(2)
        print(str(lines))
        if lines == b"\x1f\x8b":
            return True
        else:
            return False


def create_output_dir(dir_name):
    """
    Create the output directory if it does not exist
    to hold the VCF chunks
    """
    if not os.path.exists(f"{dir_name}/vcf_chunks/"):
        try:
            os.system(f"mkdir -p {dir_name}/vcf_chunks/")
        except:
            prRed("Error: Can not create directory to hold VCF chunks")
            sys.exit(1)


def split_file_by_line(filename, n):
    """
    Split a file into n chunks by line
    """
    gzip_file = is_gzipped(filename)
    if gzip_file:
        f = gzip.open(filename, "rb")
    else:
        f = open(filename)

    f.seek(1)
    chunk_size = sum(1 for line in f) // int(n)
    print(f"Chunk size: {chunk_size}")
    print(f"Number of chunks: {n}")
    f.seek(1)
    remainder = sum(1 for line in f) % int(n)
    print(f"Remainder: {remainder}")
    f.seek(1)
    header = f.readline()
    start = 0
    for i in range(int(n)):
        if gzip_file:
            chunk = [f"#{header.decode()}"]
            for j in range(chunk_size + (i < remainder)):
                chunk.append(f.readline().decode())
            yield chunk
        else:
            chunk = [f"#{header}"]
            for j in range(chunk_size + (i < remainder)):
                chunk.append(f.readline())
            yield chunk


def chunk_vcf(vcf_file, chunks, prefix, header):
    """
    Chunk the VCF file
    """
    print(f"Chunking {vcf_file} into {chunks} chunks")
    gzip_header = is_gzipped(header)
    if gzip_header:
        header = gzip.open(header, "rb")
    else:
        header = open(header)
    for i, chunk in enumerate(split_file_by_line(vcf_file, chunks)):
        with gzip.open(f"{prefix}_{i+1}.vcf.gz", "w") as f:
            header.seek(0)
            for line in header:
                if gzip_header:
                    f.write(line)
                else:
                    f.write(line.encode())
            for line in chunk:
                f.write(line.encode())

    f.close()
    header.close()


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
    chunk_vcf(
        args.input, args.chunk, f"{args.dir}/vcf_chunks/vcf_no_header", args.header
    )
