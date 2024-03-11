################################################################################
# Rules for extracting unspliced sequences surrounding the SNPs of interest
#
# Author: Kobie Kirven
#
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
################################################################################

import os
import sys

# Get the path to the script
script_path = os.path.realpath(__file__)
src_dir = os.path.dirname(script_path)

# ---- setup ----#
# Check to see if the user only wants to use the canonical transcripts:
if config["canonical"] == True:
    gff = f"{config['tmp_dir']}/canonical_transcripts.gff3"
else:
    gff = config["gff"]

# Get what the final combined outpout will be
combine_input = expand(
    f"{config['tmp_dir']}/extracted_sequences/extracted_seqs_{{i}}.txt",
    i=range(1, config["chunks"] + 1),
)


rule get_canonical_transcripts_with_AGAT:
    # Use AGAT to keep the longest isoform for each gene to speed up the process, if the user wants to
    input:
        gff=config["gff"],
    output:
        f"{config['tmp_dir']}/canonical_transcripts.gff3",
    singularity:
        "docker://condaforge/mambaforge"
    conda:
        f"{src_dir}/../variantfoldrna/workflow/envs/agat.yaml"
    log:
        f"{config['tmp_dir']}/logs/get_canonical_transcripts_with_AGAT.log",
    shell:
        f"cd {config['tmp_dir']} && agat_sp_keep_longest_isoform.pl -gff {{input.gff}} -o {{output}} > {{log}} 2>&1"


# ---- Rules ----#
rule extract_cds_from_gff_with_gffread:
    # Extract the CDS sequences from the GFF file
    params:
        gff=gff,
        ref=config["ref_genome"],
    output:
        f"{config['tmp_dir']}/cds.fa",
    conda:
        f"{src_dir}/../variantfoldrna/workflow/envs/process_seq.yaml"
    singularity:
        "docker://condaforge/mambaforge"
    log:
        f"{config['tmp_dir']}/logs/extract_cds_from_gff_with_gffread.log",
    shell:
        f"gffread {{params.gff}} -g {{params.ref}} -x {{output}}"


rule get_table_from_gffread:
    # Get the table from the GFF file
    input:
        gtf=gff,
    output:
        f"{config['tmp_dir']}/gffread_table.txt",
    conda:
        f"{src_dir}/../variantfoldrna/workflow/envs/process_seq.yaml"
    singularity:
        "docker://condaforge/mambaforge"
    shell:
        f"gffread {{input}} --table @id,@chr,@start,@end,@strand -o {{output}}"


rule create_json_from_gffread_table:
    # Create a JSON file from the GFF table
    input:
        f"{config['tmp_dir']}/gffread_table.txt",
    output:
        f"{config['tmp_dir']}/gffread_table.json",
    conda:
        f"{src_dir}/../variantfoldrna/workflow/envs/process_seq.yaml"
    singularity:
        "docker://condaforge/mambaforge"
    shell:
        f"python3 {src_dir}/../variantfoldrna/workflow/scripts/create_json_from_gffread_table.py --table {{input}} --o {{output}}"


rule extract_sequences:
    # Extract the sequences flanking the SNP
    input:
        vcf=f"{config['tmp_dir']}/annotated_vcf_chunks_effects/vcf_no_header_{{i}}_annotated_one_per_line.txt",
        database=f"{config['tmp_dir']}/gffread_table.json",
    params:
        ref_genome=config["ref_genome"],
        flank=config["flank_len"],
    output:
        seqs=f"{config['tmp_dir']}/extracted_sequences/extracted_seqs_{{i}}.txt",
    conda:
        f"{src_dir}/../variantfoldrna/workflow/envs/process_seq.yaml"
    singularity:
        "docker://condaforge/mambaforge"
    shell:
        f"python3 {src_dir}/../variantfoldrna/workflow/scripts/get_read_data.py --vcf {{input.vcf}} --gffread {{input.database}} --ref-genome {{params.ref_genome}} --flank {{params.flank}} --o {{output.seqs}}"


rule combine_extracted_sequences:
    # Combine the extracted sequences into one file
    input:
        combine_input,
    output:
        f"{config['tmp_dir']}/extracted_flank_snp.txt",
    shell:
        "cat {input} > {output}"


rule remove_duplicates:
    # Remove duplicates from the extracted sequences
    input:
        f"{config['tmp_dir']}/extracted_flank_snp.txt",
    output:
        f"{config['tmp_dir']}/extracted_flank_snp_no_duplicates.txt",
    conda:
        f"{src_dir}/../variantfoldrna/workflow/envs/process_seq.yaml"
    singularity:
        "docker://condaforge/mambaforge"
    shell:
        f"python3 {src_dir}/../variantfoldrna/workflow/scripts/remove_duplicates.py -i {{input}} -o {{output}}"
