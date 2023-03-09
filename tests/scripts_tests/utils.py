import random

def generate_dummy_vcf(num_variants, filename):
    # Generate random chromosome name and position for the variants
    chromosome = f"chr{random.randint(1, 22)}"
    positions = random.sample(range(1, 1000000), num_variants)

    vcf_lines = ["#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n"]
    # Generate fake variants with random base changes
    for i, pos in enumerate(positions):
        ref = random.choice(['A', 'C', 'G', 'T'])
        alt = random.choice(['A', 'C', 'G', 'T'])
        while alt == ref:
            alt = random.choice(['A', 'C', 'G', 'T'])
        vcf_line = f"{chromosome}\t{pos}\t.\t{ref}\t{alt}\t.\t.\t.\n"
        vcf_lines.append(vcf_line)

    # Write the VCF lines to a file
    with open(filename, 'w') as f:
        f.writelines(vcf_lines)
