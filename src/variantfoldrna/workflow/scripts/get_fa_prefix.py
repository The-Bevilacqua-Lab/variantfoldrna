###############################################################################
# Extract the prefix from the fasta file of extracted sequences. This is 
# important since the prefixes seem to vary wildly between differnet 
# organisms and RNA types
###############################################################################

# Imports 
from Bio import SeqIO
import argparse

# Function to extract the prefix from the fasta file
def get_fa_prefix(fasta_file):
    # Open the fasta file
    with open(fasta_file, "r") as handle:
        # Get the first sequence
        record = next(SeqIO.parse(handle, "fasta"))
        # Get the prefix
        prefix = record.id.split(":")[0] + ":"

        if len(record.id.split(":")) == 1:
            prefix = ""
            
    # Return the prefix
    return prefix

# Main function
def main():
    # Get the fasta file from the user
    parser = argparse.ArgumentParser(description="Extract the prefix from the fasta file of extracted sequences")
    parser.add_argument("fasta_file", help="Fasta file of extracted sequences")
    parser.add_argument("output_file", help="Output file to write the prefix to")
    args = parser.parse_args()
    # Get the prefix
    prefix = get_fa_prefix(args.fasta_file)
    # Print the prefix
    with open(args.output_file, "w") as handle:
        handle.write(prefix)

# run main 

if __name__ == "__main__":
    main()