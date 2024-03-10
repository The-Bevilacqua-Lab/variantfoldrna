from pyfaidx import Fasta
import random 
import argparse

def compelement_dna(dna):
    """
    Get the complement of a DNA sequence
    Parameters:
    - dna (str): DNA sequence
    Returns:
    - (str): Complement of the DNA sequence
    """
    complement = {"A": "U", "C": "G", "G": "C", "U": "A", "N": "N"}
    return "".join([complement[base.upper()] for base in dna])[::-1]

def extract_flank_sequences(vcf_file, reference_genome, output_file, flank ):
    # Open the VCF file
    vcf = open(vcf_file, 'r')

    # Open the reference genome
    ref_genome = Fasta(reference_genome)

    # Open the output file
    output = open(output_file, 'w')

    # Iterate over each variant in the VCF file
    for variant in vcf:
        # Skip the header lines
        if variant.startswith('#'):
            continue

        # Split the variant line
        variant = variant.strip().split('\t')

        # Get the chromosome, position, reference, and alternate allele
        chrom = variant[0]
        pos = int(variant[1])
        ref = variant[3].replace("T", "U")
        alt = variant[4].replace("T", "U")
        flank = int(flank)

        # Get the reference sequence
        ref_seq = ref_genome[chrom][pos-flank-1:pos+flank].seq
        print(len(ref_seq))
        flank_left = ref_seq[:flank].upper().replace("T", "U")
        flank_right = ref_seq[flank:].upper().replace("T", "U")

        
        # Random coin toss to decide whether to reverse complement the sequence
        strand = "positive"
        if random.randint(0, 1) == 1:
            flank_left = compelement_dna(flank_left)
            flank_right = compelement_dna(flank_right)
            strand = "negative"
            alt = compelement_dna(alt)
            ref = compelement_dna(ref)

        # Create the output line
        line = f'{chrom}\t{pos}\t{pos}\t{ref}\t{alt}\t{flank_left}\t{flank_right}\tNULL\tNULL\tNULL\t{strand}\n'
        
        # Write the information to the output file
        output.write(line)

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Extract sequences surrounding variants')
    parser.add_argument('--vcf', dest='vcf', help='VCF File')
    parser.add_argument('--ref-genome', dest='ref', help='Reference Genome')
    parser.add_argument('--flank', dest='flank', help='SNP flanking length')
    parser.add_argument('--o', dest='output', help='Output File')
    args = parser.parse_args()

    extract_flank_sequences(
        vcf_file = args.vcf,
        reference_genome = args.ref,
        output_file = args.output,
        flank = args.flank
    )

if __name__ == '__main__':
    main()
