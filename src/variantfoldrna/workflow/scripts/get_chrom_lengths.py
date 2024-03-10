# Get the lengths of all chromosomes in the reference genome and outout
# them to a text file. The output will be a text file with the following
# columns:
#     - chromosome name
#     - chromosome length

# ----- Import modules ----#
import argparse
from Bio import SeqIO


# ----- Parse arguments ----#
parser = argparse.ArgumentParser(
    description="Get the lengths of all chromosomes in the reference genome"
)
parser.add_argument("--ref-genome", dest="ref", help="Reference Genome")
parser.add_argument("--output", dest="output", help="Output file")

args = parser.parse_args()

# ----- Main -----#
# Get the lengths of all chromosomes in the reference genome
chrom_lengths = []
for record in SeqIO.parse(args.ref, "fasta"):
    chrom_lengths.append([record.id, len(record.seq)])

# Output the chromosome lengths to a text file
with open(args.output, "w") as f:
    for chrom in chrom_lengths:
        f.write("\t".join([str(x) for x in chrom]) + "\n")
