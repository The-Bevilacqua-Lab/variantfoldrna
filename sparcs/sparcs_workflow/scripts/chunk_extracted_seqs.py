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


def split_file_by_line(filename, n):
    n = int(n)
    with open(filename, "r") as f:
        chunk_size = sum(1 for line in f) // n
        f.seek(0)
        remainder = sum(1 for line in f) % n
        f.seek(0)
        start = 0
        for i in range(n):
            chunk = []
            for j in range(chunk_size + (i < remainder)):
                chunk.append(f.readline())
            yield chunk


if __name__ == "__main__":

    # Parse the arguments
    parser = argparse.ArgumentParser(description="Break up VCF file")
    parser.add_argument("--input", dest="input", help="input file")
    parser.add_argument("--dir", dest="dir", help="working directory")
    parser.add_argument(
        "--chunk-total", dest="chunk", help="The number of files to chop the input into"
    )
    args = parser.parse_args()

    # Make a directory to store the VCF chunks
    if not os.path.exists(f"{args.dir}/extracted_seqs_chunks/"):
        os.system(f"mkdir -p {args.dir}/extracted_seqs_chunks/")

    for i, chunk in enumerate(split_file_by_line(args.input, args.chunk)):
        with open(
            f"{args.dir}/extracted_seqs_chunks/extracted_flank_snp_{i+1}.txt", "w"
        ) as f:
            f.writelines(chunk)

    # # Split the VCF file up into smaller files
    # in_file = open(args.input, "r")
    # for i in range(1, int(args.chunk)):
    #     fn = open(f"{args.dir}/extracted_seqs_chunks/extracted_flank_snp_{i}.txt", "w")
    #     for g in range(chunk_len):
    #         fn.write(in_file.readline())
    #     fn.close()

    # # Write the last chunk to the output file
    # fn = open(
    #     f"{args.dir}/extracted_seqs_chunks/extracted_flank_snp_{int(args.chunk)}.txt", "w"
    # )
    # for line in in_file:
    #     fn.write(line)
    # fn.close()
