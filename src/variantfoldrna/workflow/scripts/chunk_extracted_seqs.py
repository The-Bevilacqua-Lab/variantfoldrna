################################################################################
# Split the file of extracted sequences into chunks
#
# Author: Kobie Kirven
# Assmann and Bevilacqua Labs
# The Penn State University
################################################################################

# -- Imports -- #
import argparse
import os

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
                chunk.append(f.readline())
            yield chunk


if __name__ == "__main__":

    # Parse the arguments
    parser = argparse.ArgumentParser(description="Break up VCF file")
    parser.add_argument("--input", dest="input", help="input file")
    parser.add_argument("--dir", dest="dir", help="working directory")
    parser.add_argument(
        "--all-alts", dest="all_alts", default=False, action="store_true"
    )
    parser.add_argument(
        "--chunk-total", dest="chunk", help="The number of files to chop the input into"
    )
    args = parser.parse_args()

    # Make a directory to store the VCF chunks
    if not os.path.exists(f"{args.dir}/extracted_seqs_chunks/"):
        os.system(f"mkdir -p {args.dir}/extracted_seqs_chunks/")

    if args.all_alts:
        filename = f"{args.dir}/extracted_sequences_all_alts/extracted_seqs_all_alts_unique_chunk_"
    else:
        filename = f"{args.dir}/extracted_seqs_chunks/extracted_flank_snp_"
    # Split the extracted sequences into chunks
    for i, chunk in enumerate(split_file_by_line(args.input, args.chunk)):
        with open(filename + f"{i+1}.txt", "w") as f:
            f.writelines(chunk)
