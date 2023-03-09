
import random

def generate_fasta_file(chrom_name, chrom_length, filename):
    nucleotides = ['A', 'T', 'C', 'G']
    with open(filename, 'w') as f:
        f.write(f'>{chrom_name}\n')
        for i in range(chrom_length):
            f.write(random.choice(nucleotides))
            if (i+1) % 60 == 0:
                f.write('\n')
        f.write('\n')

generate_fasta_file('chr1', 1500, 'chr1.fa')