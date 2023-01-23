################################################################################
# Rules for running snpEff on the VCF files
#
# Author: Kobie Kirven
# Email: kjk6173@psu.edu
#
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
################################################################################


# Config file
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

# Prefix for the VCF file
prefix = config["vcf_file"].split("/")[-1].strip(".vcf")


rule add_gtf:
    # combine the GTF file and reference genome into one file for snpEff
    params:
        gtf=config["gtf_file"],
        ref=config["ref_genome"],
        dir_name=f"{config['working_directory']}/{config['out_name']}/temp/data/{config['out_name']}",
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/add_gtf.log",
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/data/{config['out_name']}/genes.gtf.gz",
    shell:
        "cat {params.gtf} >> {params.dir_name}/genes.gtf && gzip {params.dir_name}/genes.gtf 2> {log}"


rule add_ref:
    # Add reference genome to the temp folder
    params:
        ref=config["ref_genome"],
        out_dir=f"{config['working_directory']}/{config['out_name']}/temp/data/genomes/",
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/add_ref.log",
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/data/genomes/{config['out_name']}.fa",
    shell:
        f"cp {{params.ref}} {{params.out_dir}}{config['out_name']}.fa"


rule create_config:
    # Create snpEff config file
    params:
        out_file=f"{config['working_directory']}/{config['out_name']}/temp/snpeff.config",
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/create_config.log",
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/snpeff.config",
    shell:
        f"echo {config['out_name']}.genome: {config['out_name']} >> {{params.out_file}} 2> {{log}}"


rule create_snpeff_database:
    # Create the snpEff database
    input:
        genes=f"{config['working_directory']}/{config['out_name']}/temp/data/{config['out_name']}/genes.gtf.gz",
        genome=f"{config['working_directory']}/{config['out_name']}/temp/data/genomes/{config['out_name']}.fa",
        snpeff_config=f"{config['working_directory']}/{config['out_name']}/temp/snpeff.config",
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/create_snpeff_database.log",
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/data/{config['out_name']}/snpEffectPredictor.bin",
    conda:
        "../envs/snpeff_env.yaml"
    shell:
        f"(cd {config['working_directory']}/{config['out_name']}/temp/ && snpEff build -c {{input.snpeff_config}} -gtf22 -v {config['out_name']} -noCheckCds -noCheckProtein) 2> {{log}}"


rule seperate_multi_vars:
    # Seperate multi-allelic variants
    input:
        vcf=f"{config['working_directory']}/{config['out_name']}/temp/vcf_chunks/vcf_no_header_{{i}}.vcf",
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/seperate_multi_vars/vcf_no_header_{{i}}_seperated.vcf.log",
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/vcf_chunks/vcf_no_header_{{i}}_seperated.vcf.gz",
    conda:
        "../envs/snpeff_env.yaml"
    shell:
        "vt decompose -s {input.vcf} | bgzip > {output} 2> {log} && tabix -p vcf {output} 2> {log}"


rule normalize:
    # Normalize variants after seperating multi-allelic variants
    input:
        vcf=f"{config['working_directory']}/{config['out_name']}/temp/vcf_chunks/vcf_no_header_{{i}}_seperated.vcf.gz",
        ref=config["ref_genome"],
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/normalize/vcf_no_header_{{i}}_normalized.vcf.log",
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/vcf_chunks/vcf_no_header_{{i}}_normalized.vcf",
    conda:
        "../envs/snpeff_env.yaml"
    shell:
        "bcftools norm --check-ref s --fasta-ref {input.ref} --output-type v -o {output} {input.vcf} 2> {log}"


rule run_snpeff:
    # Annotate variants with snpEff
    input:
        vcf=f"{config['working_directory']}/{config['out_name']}/temp/vcf_chunks/vcf_no_header_{{i}}_normalized.vcf",
        snpeff_config=f"{config['working_directory']}/{config['out_name']}/temp/snpeff.config",
        database=f"{config['working_directory']}/{config['out_name']}/temp/data/{config['out_name']}/snpEffectPredictor.bin",
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/run_snpeff/vcf_no_header_{{i}}_annotated.vcf.log",
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/annotated_vcf_chunks/vcf_no_header_{{i}}_annotated.vcf",
    conda:
        "../envs/snpeff_env.yaml"
    shell:
        f"snpEff ann -c {{input.snpeff_config}} -noStats -canon -no-upstream -no-downstream -no-intergenic {config['out_name']} {{input.vcf}} > {{output}} 2> {{log}}"


rule get_annotations_one_per_line:
    # Seperate multiple snpEff annotations into one annotation per line
    input:
        vcf=f"{config['working_directory']}/{config['out_name']}/temp/annotated_vcf_chunks/vcf_no_header_{{i}}_annotated.vcf",
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/get_annotations_one_per_line/vcf_no_header_{{i}}_annotated_one_per_line.vcf.log",
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/annotated_vcf_chunks_effects/vcf_no_header_{{i}}_annotated_one_per_line.txt",
    conda:
        "../envs/snpeff_env.yaml"
    shell:
        f'cat {{input}} | {path}/workflow/scripts/vcfEffOnePerLine.pl | SnpSift extractFields - CHROM POS REF ALT "ANN[*].EFFECT" "ANN[*].FEATUREID" > {{output}} 2> {{log}}'
