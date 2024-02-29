#############################################################
# Rules for running VEP
############################################################

# Path to the config file
configfile: srcdir("../config.yaml")

kind = "gff"
gff_file = config['gff_file']

# Check to see if the user only wants to use the canonical transcripts:
if config["canonical"] == True:
    gff_file = f"{config['working_directory']}/{config['out_name']}/temp/canonical_transcripts.gff3"
else:
    gff_file = gff_file

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
        f"{config['working_directory']}/{config['out_name']}/temp/annotation.sorted.{kind}.gz.csi"
    singularity:
        "docker://ensemblorg/ensembl-vep:release_100.2"
    shell:
        "tabix --csi -p gff {input.annotation}"

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
        "vt decompose -s {input.vcf} 2> {log} | bgzip > {output} 2> {log} && tabix --csi -p vcf {output} 2> {log}"


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

if config['variant_class'] != "None":
    grep_command = f" grep -v '##' | grep -v 'stream_gene_variant' | grep -v 'intergenic' | grep -v 'coding_sequence_variant' | grep {config['variant_class']} ",
else:
    grep_command = f" grep -v '##' | grep -v 'stream_gene_variant' | grep -v 'intergenic' | grep -v 'coding_sequence_variant' "

rule vep:
    # Run VEP on the VCF file and output a TAB file with the annotations
    input:
        vcf=f"{config['working_directory']}/{config['out_name']}/temp/vcf_chunks/vcf_no_header_{{i}}_normalized.vcf",
        annotation=f"{config['working_directory']}/{config['out_name']}/temp/annotation.sorted.{kind}.gz",
        fasta = config["ref_genome"],
        tbi = f"{config['working_directory']}/{config['out_name']}/temp/annotation.sorted.{kind}.gz.csi"
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/annotated_vcf_chunks_effects/vcf_no_header_{{i}}_annotated_one_per_line.txt",
    params:
        output = f"{config['working_directory']}/{config['out_name']}/temp/annotated_vcf_chunks_effects/vcf_no_header_{{i}}_annotated_one_per_line_temp.txt",
        grep_command = f"{grep_command}"
    singularity:
        "docker://ensemblorg/ensembl-vep:release_100.2"
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/vep/vcf_no_header_{{i}}_annotated_one_per_line.log"
    shell:
        f'vep -i {{input.vcf}} --{kind} {{input.annotation}} --fasta {{input.fasta}} -o {{params.output}} --force_overwrite --tab --fields "Location,REF_ALLELE,Allele,Consequence,Feature,cDNA_position,HGVSc,STRAND,CANONICAL" --hgvs --show_ref_allele --canonical 2> {{log}}   && cat {{params.output}} | {{params.grep_command}}  > {{output}}'
