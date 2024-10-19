################################################################################
# Split the input CSV file into chunks
#
# Author: Kobie Kirven
# Assmann and Bevilacqua Labs
# The Penn State University
################################################################################

# -- Imports -- #
import argparse
import os
import sys

#######################
#  --  Functions --   #
#######################


def split_file_by_line(filename, n):
    """Split a file into n chunks by line"""
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
                line = f.readline()
                if "FLANK" not in line:
                    chunk.append(line)
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
    if not os.path.exists(f"{args.dir}/csv_chunks/"):
        os.system(f"mkdir -p {args.dir}/csv_chunks/")

    filename = f"{args.dir}/csv_chunks/csv_chunk_"

    # Count the number of lines in the file and make sure it is not more than the number of chunks
    with open(args.input, "r") as f:
        total_lines = sum(1 for line in f)
    if total_lines < int(args.chunk):
        print("The number of chunks must be less than the number of lines in the file.")
        sys.exit(1)

    # Split the CSV file into chunks
    for i, chunk in enumerate(split_file_by_line(args.input, args.chunk)):
        with open(filename + f"{i+1}.csv", "w") as f:
            f.writelines(chunk)
