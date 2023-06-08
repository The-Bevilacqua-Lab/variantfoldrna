################################################################################
# Rules for extracting unspliced sequences surrounding the SNPs of interest
#
# Author: Kobie Kirven
#
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
################################################################################


#---- Imports ----#
import os

# Read in the config file:
configfile: srcdir("../config.yaml")

#---- setup ----#
# Check to see if the user only wants to use the canonical transcripts:
if config["canonical"] == True:
    gff_file = f"{config['working_directory']}/{config['out_name']}/temp/canonical_transcripts.gff3"
else:
    gff_file = config["gff_file"]

# Get what the final combined outpout will be
combine_input = expand(
    f"{config['working_directory']}/{config['out_name']}/temp/extracted_sequences/extracted_seqs_{{i}}.txt",
    i=range(1, config["chunks"] + 1),
)

#---- Rules ----#
rule extract_cds_from_gff_with_gffread:
    # Extract the CDS sequences from the GFF file
    params:
        gff=gff_file,
        ref=config["ref_genome"],
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/cds.fa",
    singularity:
        "docker://kjkirven/process_seq"
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/extract_cds_from_gff_with_gffread.log"
    shell:
        f"gffread {{params.gff}} -g {{params.ref}} -x {{output}}"

rule get_table_from_gffread:
    # Get the table from the GFF file
    input:
        gtf=gff_file,
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/gffread_table.txt",
    singularity:
        "docker://kjkirven/process_seq"
    shell:
        f"gffread {{input}} --table @id,@chr,@start,@end,@strand -o {{output}}"

rule create_json_from_gffread_table:
    # Create a JSON file from the GFF table
    input:
        f"{config['working_directory']}/{config['out_name']}/temp/gffread_table.txt",
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/gffread_table.json",
    singularity:
        "docker://kjkirven/process_seq"
    shell:
        f"python3 scripts/create_json_from_gffread_table.py --table {{input}} --o {{output}}"

rule extract_sequences:
    # Extract the sequences flanking the SNP
    input:
        vcf=f"{config['working_directory']}/{config['out_name']}/temp/annotated_vcf_chunks_effects/vcf_no_header_{{i}}_annotated_one_per_line.txt",
        database=f"{config['working_directory']}/{config['out_name']}/temp/gffread_table.json",
    params:
        ref_genome=config["ref_genome"],
        flank=config["flank_len"],
    output:
        seqs=f"{config['working_directory']}/{config['out_name']}/temp/extracted_sequences/extracted_seqs_{{i}}.txt",
    singularity:
        "docker://kjkirven/process_seq"
    shell:
        f"python3 scripts/get_read_data.py --vcf {{input.vcf}} --gffread {{input.database}} --ref-genome {{params.ref_genome}} --flank {{params.flank}} --o {{output.seqs}}"


rule combine_extracted_sequences:
    # Combine the extracted sequences into one file
    input:
        combine_input
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
    singularity:
        "docker://kjkirven/process_seq"
    shell:
        f"python3 scripts/remove_duplicates.py -i {{input}} -o {{output}}"
