################################################################################
# Rules for extracting sequences from the reference genome
#
# Author: Kobie Kirven
#
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
################################################################################

# Read in the config file:
configfile: srcdir("../config.yaml")

# Import the python modules:
import os

rule create_gffutils:
    # Create the gffutils database
    params:
        gtf=config["gtf_file"],
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/{config['gtf_file'].split('/')[-1].strip('.gtf')}.db",
    conda:
        "../envs/extract_seqs.yaml"
    shell:
        f"python3 workflow/scripts/build_gffutils.py --gtf {{params.gtf}} --o {{output}}"


rule extract_sequences:
    # Extract the sequences flanking the SNP
    input:
        vcf=f"{config['working_directory']}/{config['out_name']}/temp/annotated_vcf_chunks_effects/vcf_no_header_{{i}}_annotated_one_per_line.txt",
        database=f"{config['working_directory']}/{config['out_name']}/temp/{config['gtf_file'].split('/')[-1].strip('.gtf')}.db",
    params:
        ref_genome=config["ref_genome"],
        flank=config["flank_len"],
    output:
        seqs = f"{config['working_directory']}/{config['out_name']}/temp/extracted_sequences/extracted_seqs_{{i}}.txt",
    conda:
        "../envs/extract_seqs.yaml"
    shell:
        f"python3 workflow/scripts/get_read_data.py --vcf {{input.vcf}} --database {{input.database}} --ref-genome {{params.ref_genome}} --flank {{params.flank}} --o {{output.seqs}}"


rule combine_extracted_sequences:
    # Combine the extracted sequences into one file
    input:
        expand(
            f"{config['working_directory']}/{config['out_name']}/temp/extracted_sequences/extracted_seqs_{{i}}.txt",
            i=range(1, config["chunks"] + 1),
        ),
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/extracted_flank_snp.txt",
    shell:
        "cat {input} > {output}"


rule remove_duplicates:
    # Remove duplicates from the extracted sequences
    input:
        f"{config['working_directory']}/{config['out_name']}/temp/extracted_flank_snp.txt",
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/extracted_flank_snp_no_duplicates.txt",
    conda:
        "../envs/extract_seqs.yaml"
    shell:
        f"python3 workflow/scripts/remove_duplicates.py -i {{input}} -o {{output}}"
