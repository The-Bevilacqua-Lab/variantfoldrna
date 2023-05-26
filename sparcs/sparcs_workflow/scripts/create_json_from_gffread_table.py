################################################################################
# Convert a gffread table to a json file
#
# Author: Kobie Kirven
################################################################################

# ----- Import modules ----#
import argparse
import json

# ----- Functions ------#
def gffread_table_to_json(gffread_table):
    gene_dict = {}
    with open(gffread_table) as fn:
        for line in fn:
            gene_dict[line.split("\t")[0].split(":")[-1]] = [line.split("\t")[1], int(line.split("\t")[2]), int(line.split("\t")[3])]
    return gene_dict

# -- main --#

if __name__ == "__main__":

    # ----- Parse arguments ----#
    parser = argparse.ArgumentParser(
        description="Convert a gffread table to a json file"
    )
    parser.add_argument(
        "--table", dest="gffread_table", help="gffread table"
    )
    parser.add_argument(
        "--output", dest="output", help="Output file"
    )
    args = parser.parse_args()

    # Create the dictionary
    gene_dict = gffread_table_to_json(args.gffread_table)

    # Serialize the dictionary
    with open(args.output, "w") as fn:
        json.dump(gene_dict, fn)
