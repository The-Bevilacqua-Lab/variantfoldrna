################################################################################
# Rules for extracting sequences from the reference genome
#
# Author: Kobie Kirven
#
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
################################################################################


configfile: srcdir("../config.yaml")


# Import the python modules:
import os

# Get the location of this file:
location = os.getcwd()

# Get the path up to the SPARCS directory:
path = []
for ele in location.split("/"):
    if ele == "SPARCS":
        path.append(ele)
        break
    else:
        path.append(ele)

# Convert the path to a string:
path = "/".join(path)


rule create_gffutils:
    # Create the gffutils database
    params:
        gtf=config["gtf_file"],
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/{config['gtf_file'].split('/')[-1].strip('.gtf')}.db",
    conda:
        "../envs/extract_seqs.yaml"
    shell:
        f"python3 {path}/workflow/scripts/build_gffutils.py --gtf {{params.gtf}} --o {{output}}"


rule extract_sequencs:
    # Extract the sequences flanking the SNP
    input:
        vcf=f"{config['working_directory']}/{config['out_name']}/temp/annotated_vcf_chunks_effects/vcf_no_header_{{i}}_annotated_one_per_line.txt",
        database=f"{config['working_directory']}/{config['out_name']}/temp/{config['gtf_file'].split('/')[-1].strip('.gtf')}.db",
    params:
        ref_genome=config["ref_genome"],
        flank=config["flank_len"],
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/extracted_sequences/extracted_seqs_{{i}}.txt",
    conda:
        "../envs/extract_seqs.yaml"
    shell:
        f"python3 {path}/workflow/scripts/get_read_data.py --vcf {{input.vcf}} --database {{input.database}} --ref-genome {{params.ref_genome}} --flank {{params.flank}} --o {{output}}"


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
    shell:
        f"python3 {path}/workflow/scripts/remove_duplicates.py -i {{input}} -o {{output}}"