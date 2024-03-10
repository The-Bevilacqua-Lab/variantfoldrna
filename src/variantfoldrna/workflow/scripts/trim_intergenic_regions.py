#python3 workflow/scripts/trim_intergenic_regions.py --input {input.gene_model} --output {output}

# Trim the intergenic regions from the bedtools complement of the gene model

# imports 
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Trim the intergenic regions from the bedtools complement of the gene model')
    parser.add_argument('--input', required=True, help='Input gene model file')
    parser.add_argument('--output', required=True, help='Output gene model file')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    o = open(args.output, 'w')
    with open(args.input, 'r') as f:
        for line in f:
            chrom = line.split('\t')[0]
            start = int(line.split('\t')[1])
            end = int(line.split('\t')[2])

            if end - start < 1000:
                continue
            else:
                with open(args.output, 'a') as o:
                    o.write(f"{chrom}\t{start}\t{end-1000}\n")
    o.close()

if __name__ == "__main__":
    main()

    