#############################################################
# Rules for running VEP
############################################################

# Path to the config file
configfile: srcdir("../config.yaml")

# Check to see if the user input a GTF or a GFF file
if config["gtf_file"] != "None":
    annotation = config["gtf_file"]
    kind = "gtf"
else:
    annotation = config["gff_file"]
    kind = "gff"

# Check to see if the user only wants to use the canonical transcripts:
if config["canonical"] == True:
    gff_file = f"{config['working_directory']}/{config['out_name']}/temp/canonical_transcripts.gff3"
    print("YES")
else:
    gff_file = annotation


rule sort_gene_model:
    input:
        gff_file
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/annotation.sorted.{kind}.gz"
    singularity:
        "docker://ensemblorg/ensembl-vep:release_100.2"
    shell:
        "grep -v '#' {input} | sort -k1,1 -k4,4n -k5,5n -t$'\t' | bgzip -c > {output}"

rule tabix_annotation:
    input:
        annotation = f"{config['working_directory']}/{config['out_name']}/temp/annotation.sorted.{kind}.gz"
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/annotation.sorted.{kind}.gz.tbi"
    singularity:
        "docker://ensemblorg/ensembl-vep:release_100.2"
    shell:
        "tabix -p gff {input.annotation}"

rule seperate_multi_vars:
    # Seperate multi-allelic variants
    input:
        vcf=f"{config['working_directory']}/{config['out_name']}/temp/vcf_chunks/vcf_no_header_{{i}}.vcf.gz",
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/seperate_multi_vars/vcf_no_header_{{i}}_seperated.vcf.log",
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/vcf_chunks/vcf_no_header_{{i}}_seperated.vcf.gz",
    singularity:
        "docker://kjkirven/snpeff"
    shell:
        "vt decompose -s {input.vcf} 2> {log} | bgzip > {output} 2> {log} && tabix -p vcf {output} 2> {log}"


rule normalize:
    # Normalize variants after seperating multi-allelic variants
    input:
        vcf=f"{config['working_directory']}/{config['out_name']}/temp/vcf_chunks/vcf_no_header_{{i}}_seperated.vcf.gz",
        ref=config["ref_genome"],
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/normalize/vcf_no_header_{{i}}_normalized.vcf.log",
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/vcf_chunks/vcf_no_header_{{i}}_normalized.vcf",
    singularity:
        "docker://kjkirven/snpeff"
    shell:
        "bcftools norm --check-ref s --fasta-ref {input.ref} --output-type v -o {output} {input.vcf} 2> {log}"

rule vep:
    # Run VEP on the VCF file and output a TAB file with the annotations
    input:
        vcf=f"{config['working_directory']}/{config['out_name']}/temp/vcf_chunks/vcf_no_header_{{i}}_normalized.vcf",
        annotation=f"{config['working_directory']}/{config['out_name']}/temp/annotation.sorted.{kind}.gz",
        fasta = config["ref_genome"],
        tbi = f"{config['working_directory']}/{config['out_name']}/temp/annotation.sorted.{kind}.gz.tbi"
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/annotated_vcf_chunks_effects/vcf_no_header_{{i}}_annotated_one_per_line.txt",
    params:
        f"{config['working_directory']}/{config['out_name']}/temp/annotated_vcf_chunks_effects/vcf_no_header_{{i}}_annotated_one_per_line_temp.txt",
    singularity:
        "docker://ensemblorg/ensembl-vep:release_100.2"
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/vep/vcf_no_header_{{i}}_annotated_one_per_line.log"
    shell:
        f'vep -i {{input.vcf}} --{kind} {{input.annotation}} --fasta {{input.fasta}} -o {{params}} --force_overwrite --tab --fields "Location,REF_ALLELE,Allele,Consequence,Feature,cDNA_position,HGVSc,STRAND,CANONICAL" --hgvs --show_ref_allele --canonical && cat {{params}} | grep -v "##" | grep -v "stream_gene_variant" | grep -v "intergenic" > {{output}}'


