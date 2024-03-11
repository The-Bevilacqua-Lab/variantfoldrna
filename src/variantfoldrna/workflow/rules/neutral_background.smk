################################################################################
#
# Rules for creating the null model to compare against.
#
# Author: Kobie Kirven
#
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
################################################################################

# ---- imports ----#
import os
import sys

# Get the path to the script
script_path = os.path.realpath(__file__)
src_dir = os.path.dirname(script_path)


# Create a rule to complement the input gene model so that we get the
# putative intergenic regions.
rule get_bedtools_genome_file:
    params:
        ref=config["ref_genome"],
    output:
        f"{config['tmp_dir']}/genome_bedtools_file.txt",
    log:
        f"{config['tmp_dir']}/logs/get_bedtools_genome_file.log",
    singularity:
        "docker://kjkirven/process_seq"
    shell:
        f"python3 {src_dir}/../variantfoldrna/workflow/scripts/get_chrom_lengths.py --ref-genome {params.ref} --output {output}"


rule convert_gff_to_bed:
    input:
        gff=config["gff"],
    output:
        f"{config['tmp_dir']}/gene_model.bed",
    log:
        f"{config['tmp_dir']}/logs/convert_gff_to_bed.log",
    singularity:
        "docker://quay.io/biocontainers/agat:1.0.0--pl5321hdfd78af_0"
    shell:
        "agat_convert_sp_gff2bed.pl --gff {input.gff} -o {output} &&  cat {output} | cut -f1-3 > {output}.tmp && mv {output}.tmp {output}"


rule sort_gene_model_null:
    input:
        gene_model=f"{config['tmp_dir']}/gene_model.bed",
    output:
        f"{config['tmp_dir']}/gene_model_sorted.bed",
    log:
        f"{config['tmp_dir']}/logs/sort_gene_model.log",
    singularity:
        "docker://quay.io/staphb/bedtools"
    shell:
        "sortBed -i {input.gene_model} > {output}"


rule sort_genome_file:
    input:
        ref=f"{config['tmp_dir']}/genome_bedtools_file.txt",
    output:
        f"{config['tmp_dir']}/genome_bedtools_file_sorted.txt",
    log:
        f"{config['tmp_dir']}/logs/sort_genome_file.log",
    singularity:
        "docker://quay.io/staphb/bedtools"
    shell:
        "sort -k1,1 -k4,4n {input.ref} > {output}"


rule complement_gene_model:
    input:
        ref=f"{config['tmp_dir']}/genome_bedtools_file_sorted.txt",
        gff=f"{config['tmp_dir']}/gene_model_sorted.bed",
    output:
        f"{config['tmp_dir']}/gene_model_complement.bed",
    log:
        f"{config['tmp_dir']}/logs/complement_gene_model.log",
    singularity:
        "docker://quay.io/staphb/bedtools"
    shell:
        "bedtools complement -i {input.gff} -g {input.ref} > {output}"


rule trim_intergenic_regions:
    # trim the intergenic regions to avoid promoters
    input:
        gene_model=f"{config['tmp_dir']}/gene_model_complement.bed",
    output:
        f"{config['tmp_dir']}/gene_model_complement_trimmed.bed",
    log:
        f"{config['tmp_dir']}/logs/trim_intergenic_regions.log",
    singularity:
        "docker://kjkirven/process_seq"
    shell:
        f"python3 {src_dir}/../variantfoldrna/workflow/scripts/trim_intergenic_regions.py --input {input.gene_model} --output {output}"


rule bgzip_vcf:
    params:
        vcf=config["vcf"],
        bgzip=f"{config['tmp_dir']}/bgzip_{config['vcf']}",
    output:
        f"{config['tmp_dir']}/bgzip_{config['vcf']}.gz",
    log:
        f"{config['tmp_dir']}/logs/bgzip_vcf.log",
    singularity:
        "docker://kjkirven/snpeff"
    shell:
        "cp {params.vcf} {params.bgzip} && bgzip {params.bgzip} && tabix -p vcf {params.bgzip}.gz"


rule intersect_vcf_with_gene_model:
    input:
        gene_model=f"{config['tmp_dir']}/gene_model_complement_trimmed.bed",
        vcf=f"{config['tmp_dir']}/bgzip_{config['vcf']}.gz",
    output:
        f"{config['tmp_dir']}/intergenic_variants.vcf",
    log:
        f"{config['tmp_dir']}/logs/intersect_vcf_with_gene_model.log",
    singularity:
        "docker://kjkirven/snpeff"
    shell:
        "bcftools view -R {input.gene_model} {input.vcf} > {output}"


rule extract_flank_sequences_null:
    input:
        ref=config["ref_genome"],
        vcf=f"{config['tmp_dir']}/intergenic_variants.vcf",
    output:
        f"{config['tmp_dir']}/intergenic_flank_seq.txt",
    log:
        f"{config['tmp_dir']}/logs/extract_flank_sequences.log",
    singularity:
        "docker://kjkirven/process_seq"
    shell:
        f"python3 {src_dir}/../variantfoldrna/workflow/scripts/extract_flank_sequences_null.py --ref-genome {input.ref} --vcf {input.vcf} --o {output} --flank 50"


rule get_bakground_mutation_rate:
    input:
        f"{config['tmp_dir']}/intergenic_flank_seq.txt",
    output:
        f"{config['tmp_dir']}/background_mutation_rate.txt",
    log:
        f"{config['tmp_dir']}/logs/get_background_mutation_rate.log",
    singularity:
        "docker://kjkirven/process_seq"
    shell:
        f"python3 {src_dir}/../variantfoldrna/workflow/scripts/get_background_mutation_rate.py --input {input} --output {output}"
