import argparse

def replace_info_with_period(input_vcf, output_vcf):
    with open(input_vcf, 'r') as input_file, open(output_vcf, 'w') as output_file:
        for line in input_file:
            if line.startswith('#'):
                # Write header lines unchanged
                output_file.write(line)
            else:
                fields = line.strip().split('\t')
                info_field = fields[7]  # INFO field is at index 7
                new_info_field = '.'    # Replace INFO with '.'
                fields[7] = new_info_field
                output_file.write('\t'.join(fields) + '\n')

def main():
    parser = argparse.ArgumentParser(description="Replace INFO fields in a VCF file with '.'")
    parser.add_argument("input_vcf", help="Input VCF file")
    parser.add_argument("output_vcf", help="Output VCF file with replaced INFO fields")

    args = parser.parse_args()

    replace_info_with_period(args.input_vcf, args.output_vcf)

    print("INFO fields replaced with '.' in the output VCF file.")

if __name__ == "__main__":
    main()