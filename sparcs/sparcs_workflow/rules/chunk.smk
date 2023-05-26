################################################################################
# Rules for breaking up files into smaller, more managable chunks
#
# Author: Kobie Kirven
#
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
################################################################################
configfile: srcdir("../config.yaml")


# Import the python modules:
import os


rule chunk_vcf:
    # Break up the VCF file in to bite-sized chunks so that it is easier to process
    input:
        vcf=f"{config['working_directory']}/{config['out_name']}/temp/vcf_no_header.vcf.gz",
        header=f"{config['working_directory']}/{config['out_name']}/temp/vcf_header.txt.gz",
    output:
        expand(
            f"{config['working_directory']}/{config['out_name']}/temp/vcf_chunks/vcf_no_header_{{i}}.vcf.gz",
            i=range(1, int(config["chunks"]) + 1),
        ),
    singularity:
        "docker://kjkirven/process_seq"
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/chunk_vcf.log"
    shell:
        f"python3 scripts/chunk_vcf.py --input {{input.vcf}} --dir {config['working_directory']}/{config['out_name']}/temp --vcf-header {{input.header}} --chunk-total {config['chunks']} > {{log}}"


rule chunk_extracted_sequences:
    # Chunk the extracted sequences:
    input:
        f"{config['working_directory']}/{config['out_name']}/temp/extracted_flank_snp_no_duplicates.txt",
    output:
        expand(
            f"{config['working_directory']}/{config['out_name']}/temp/extracted_seqs_chunks/extracted_flank_snp_{{i}}.txt",
            i=range(1, config["chunks"] + 1),
        ),
    singularity:
        "docker://kjkirven/process_seq"
    shell:
        f"python3 scripts/chunk_extracted_seqs.py --input {{input}} --dir {config['working_directory']}/{config['out_name']}/temp --chunk-total {config['chunks']}"
