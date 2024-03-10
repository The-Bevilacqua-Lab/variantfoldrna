################################################################################
# Generate all possible mutations based on a given VCF file
# Author: Kobie Kirven
#
################################################################################

# Imports
import argparse


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Generate all possible mutations based on a given VCF file."
    )
    parser.add_argument("-i", "--input", help="Input file name", required=True)
    parser.add_argument("-o", "--output", help="Output file name", required=True)
    args = parser.parse_args()

    # Open the output file
    output_file = open(args.output, "w")

    # Open the input file
    with open(args.input, "r") as input_file:
        for line in input_file:
            # Skip header
            if line.startswith("#"):
                output_file.write(line)
                continue

            # Split the line
            line = line.strip().split("\t")

            alts = ["A", "C", "G", "T"]

            for alt in alts:
                if alt == line[4]:
                    continue
                if line[3] == alt:
                    continue
                else:
                    # Write the line
                    output_file.write(
                        "\t".join(line[:4])
                        + "\t"
                        + alt
                        + "\t"
                        + "\t".join(line[5:])
                        + "\n"
                    )

    # Close the output file
    output_file.close()


if __name__ == "__main__":
    main()
