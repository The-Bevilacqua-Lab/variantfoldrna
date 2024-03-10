import random
import argparse

# Step 1: Parse command-line arguments
parser = argparse.ArgumentParser(description='Get a random subset of variants from a VCF file')
parser.add_argument('--vcf', help='Path to the input VCF file', required=True)
parser.add_argument('--output', help='Path to the output VCF file', required=True)
parser.add_argument('--subset-size', type=int, help='Number of variants to include in the subset', default=100)
args = parser.parse_args()

input_file = args.vcf
output_file = args.output
subset_size = args.subset_size

# Step 2: Read the input VCF file
with open(input_file, 'r') as f:
    vcf_lines = f.readlines()

# Step 3: Parse the header of the VCF file
header_lines = []
variant_lines = []
for line in vcf_lines:
    if line.startswith('#'):
        header_lines.append(line)
    else:
        variant_lines.append(line)

# Step 4: Get the total number of variants in the VCF file
num_variants = len(variant_lines)

# Step 5: Generate a random set of indices to select the variants for the subset
random_indices = random.sample(range(num_variants), subset_size)

# Step 6: Create a new VCF file and write the header to it
with open(output_file, 'w') as f:
    f.writelines(header_lines)

    # Step 7: Iterate through the variants and write the selected variants to the new VCF file
    for index in random_indices:
        f.write(variant_lines[index])

# Step 8: Close the input and output files
f.close()