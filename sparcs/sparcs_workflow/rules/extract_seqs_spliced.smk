################################################################################
# Rules for extracting sequences from the reference genome
#
# Author: Kobie Kirven
#
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
################################################################################

#---- imports ----#

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

#---- rules ----#
rule get_canonical_transcripts_with_AGAT:
    # Use AGAT to keep the longest isoform for each gene to speed up the process, if the user wants to
    input:
        gff=config["gff_file"],
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/canonical_transcripts.gff3"
    singularity:
        "docker://quay.io/biocontainers/agat:1.0.0--pl5321hdfd78af_0"
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/get_canonical_transcripts_with_AGAT.log"
    shell:
        f"cd {config['working_directory']} && agat_sp_keep_longest_isoform.pl -gff {{input.gff}} -o {{output}} > {{log}} 2>&1"

rule get_table_from_gffread:
    # Get the table from the GFF file
    input:
        gff=gff_file,
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
        f"python3 workflow/scripts/create_json_from_gffread_table.py --table {{input}} --o {{output}}"

rule extract_cdna_from_gff_with_gffread:
    # Extract the cDNA sequences from the GFF file
    input:
        gff=gff_file,
    params:
        ref=config["ref_genome"],
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/cdna.fa",
    singularity:
        "docker://kjkirven/process_seq"
    shell:
        f"gffread {{input.gff}} -g {{params.ref}} -w {{output}}"

rule get_cds_start:
    input:
        f"{config['working_directory']}/{config['out_name']}/temp/cdna.fa",
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/cdna_pos.txt",
    shell:
        "cat {input} | grep '>' > {output}"

rule extract_spliced_sequences:
    # Extract the sequences flanking the SNP
    input:
        vcf=f"{config['working_directory']}/{config['out_name']}/temp/annotated_vcf_chunks_effects/vcf_no_header_{{i}}_annotated_one_per_line.txt",
        cds_pos=f"{config['working_directory']}/{config['out_name']}/temp/cdna_pos.txt",
        cdna = f"{config['working_directory']}/{config['out_name']}/temp/cdna.fa",
        database=f"{config['working_directory']}/{config['out_name']}/temp/gffread_table.json",
    params:
        flank=config["flank_len"],
    output:
        seqs=f"{config['working_directory']}/{config['out_name']}/temp/extracted_sequences/extracted_seqs_{{i}}.txt",
    singularity:
        "docker://kjkirven/process_seq"
    shell:
        f"python3 workflow/scripts/get_spliced_read_data.py --vcf {{input.vcf}} --ref-seqs {{input.cdna}} --flank {{params.flank}} --gffread {{input.database}} --cds-pos {{input.cds_pos}} --o {{output.seqs}}"

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
        f"python3 workflow/scripts/remove_duplicates.py -i {{input}} -o {{output}}"