################################################################################
# 
# Rules for creating the null model to compare against. 
# 
# Author: Kobie Kirven
#
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
################################################################################

#---- imports ----#

# Read in the config file:
configfile: srcdir("../config.yaml")

# Create a rule to complement the input gene model so that we get the 
# putative intergenic regions.
rule get_bedtools_genome_file:
    params:
        ref=config["ref_genome"]
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/genome_bedtools_file.txt"
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/get_bedtools_genome_file.log"
    singularity:
        "docker://kjkirven/process_seq"
    shell:
        "python3 workflow/scripts/get_chrom_lengths.py --ref-genome {params.ref} --output {output}"

rule convert_gff_to_bed:
    input:
        gff_file = config["gff_file"]
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/gene_model.bed"
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/convert_gff_to_bed.log"
    singularity:
        "docker://quay.io/biocontainers/agat:1.0.0--pl5321hdfd78af_0"
    shell:
        "agat_convert_sp_gff2bed.pl --gff {input.gff_file} -o {output} &&  cat {output} | cut -f1-3 > {output}.tmp && mv {output}.tmp {output}"

rule sort_gene_model_null:
    input:
        gene_model = f"{config['working_directory']}/{config['out_name']}/temp/gene_model.bed"
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/gene_model_sorted.bed"
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/sort_gene_model.log"
    singularity:
        "docker://quay.io/staphb/bedtools"
    shell:
        "sortBed -i {input.gene_model} > {output}"

rule sort_genome_file:
    input:
        ref = f"{config['working_directory']}/{config['out_name']}/temp/genome_bedtools_file.txt"
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/genome_bedtools_file_sorted.txt"
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/sort_genome_file.log"
    singularity:
        "docker://quay.io/staphb/bedtools"
    shell:
        "sort -k1,1 -k4,4n {input.ref} > {output}"

rule complement_gene_model:
    input:
        ref = f"{config['working_directory']}/{config['out_name']}/temp/genome_bedtools_file_sorted.txt",
        gff_file = f"{config['working_directory']}/{config['out_name']}/temp/gene_model_sorted.bed"
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/gene_model_complement.bed"
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/complement_gene_model.log"
    singularity:
        "docker://quay.io/staphb/bedtools"
    shell:
        "bedtools complement -i {input.gff_file} -g {input.ref} > {output}"

rule bgzip_vcf:
    params:
        vcf_file = config["vcf_file"]
    output:
        f"{config['vcf_file']}.gz"
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/bgzip_vcf.log"
    singularity:
        "docker://kjkirven/snpeff"
    shell:
        "bgzip {params.vcf_file} && tabix -p vcf {params.vcf_file}.gz"

rule intersect_vcf_with_gene_model:
    input:
        gene_model = f"{config['working_directory']}/{config['out_name']}/temp/gene_model_complement.bed",
        vcf_file = f"{config['vcf_file']}.gz"
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/intergenic_variants.vcf"
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/intersect_vcf_with_gene_model.log"
    singularity:
        "docker://kjkirven/snpeff"
    shell:
        "bcftools view -R {input.gene_model} {input.vcf_file} > {output}"

rule get_random_subset_of_variants:
    input:
        vcf_file = f"{config['working_directory']}/{config['out_name']}/temp/intergenic_variants.vcf"
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/intergenic_variants_subset.vcf"
    params:
        subset_size = config["subset_size"]
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/get_random_subset_of_variants.log"
    singularity:
        "docker://kjkirven/snpeff"
    shell:  
        "python3 workflow/scripts/get_random_subset_vcf.py --vcf {input.vcf_file} --output {output} --subset-size {params.subset_size}"

rule extract_flank_sequences_null:
    input:
        ref = config["ref_genome"],
        vcf_file = f"{config['working_directory']}/{config['out_name']}/temp/intergenic_variants_subset.vcf"
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/intergenic_flank_seq.txt"
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/extract_flank_sequences.log"
    singularity:
        "docker://kjkirven/process_seq"
    shell:
        "python3 workflow/scripts/extract_flank_sequences_null.py --ref-genome {input.ref} --vcf {input.vcf_file} --o {output} --flank 50"

rule chunk_extracted_sequences_null:
    # Chunk the extracted sequences:
    input:
        f"{config['working_directory']}/{config['out_name']}/temp/intergenic_flank_seq.txt"
    output:
        expand(
            f"{config['working_directory']}/{config['out_name']}/temp/null/extracted_seqs_chunks/extracted_flank_snp_{{i}}.txt",
            i=range(1, config["chunks"] + 1),
        ),
    singularity:
        "docker://kjkirven/process_seq"
    shell:
        f"python3 workflow/scripts/chunk_extracted_seqs.py --input {{input}} --dir {config['working_directory']}/{config['out_name']}/temp/null --chunk-total {config['chunks']}"
        
rule run_snpfold_null:
    # Perform the riboSNitch analysis with SNPFold
    input:
        f"{config['working_directory']}/{config['out_name']}/temp/null/extracted_seqs_chunks/extracted_flank_snp_{{i}}.txt",
    params:
        f"{{temp_deg}}",
    output:
        ribo=f"{config['working_directory']}/{config['out_name']}/temp/null_{{temp_deg}}/chunk_{{i}}_riboSNitch_null_{{temp_deg}}.txt",
        error=f"{config['working_directory']}/{config['out_name']}/temp/null_{{temp_deg}}/chunk_{{i}}_riboSNitch_null_{{temp_deg}}_error.txt",
    singularity:
        "docker://kjkirven/snpfold:latest"
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/ribosnitch_prediction/chunk_{{i}}_riboSNitch_null_{{temp_deg}}.log",
    shell:
        f"python3 workflow/scripts/snpfold_wrapper.py --i {{input[0]}} --o {{output.ribo}} --flank {config['flank_len']} --temp {{params}}"

rule combine_ribosnitch_results_null:
    # Combine the results of riboSNitch prediction into one file
    input:
        [
            f"{config['working_directory']}/{config['out_name']}/temp/null_{{temp_deg}}/chunk_{i}_riboSNitch_null_{{temp_deg}}.txt"
            for i in range(1, config["chunks"] + 1)
        ],
    output:
        f"{config['working_directory']}/{config['out_name']}/results/null_model/combined_ribosnitch_prediction_null_{{temp_deg}}.txt"
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/combine_ribosnitch_results_null_{{temp_deg}}.log",
    shell:
        "echo    'Chrom	Pos	Transcript_pos	Ref	Alt	Flank_left	Flank_right	Gene	Match	Type	Strand	Score' > {output} && cat {input} >> {output}"

    

