########################################################################################################################
# Rules for running generating all possible SNPs for the covered positions in the VCF file. 
#
# Author: Kobie Kirven
# Assmann and Bevilacqua Labs -- Penn State University
########################################################################################################################

rule add_possible_alts:
    # Add possible alternative alleles to the VCF file
    input:
        vcf=f"{config['working_directory']}/{config['out_name']}/temp/vcf_chunks/vcf_no_header_{{i}}_normalized.vcf",
    message:
        "Adding possible alternative alleles to the VCF file"
    output:
        vcf=f"{config['working_directory']}/{config['out_name']}/temp/vcf_chunks_null/vcf_no_header_{{i}}_normalized_possible_alts.vcf",
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/add_possible_alts_{{i}}.log"
    singularity:
        "docker://kjkirven/process_seq"
    shell:
        "python3 workflow/scripts/generate_all_mutations.py --input {input} --output {output}"

rule create_vep_other_alts_dir:
    # Create the directory for the VEP annotations for the generated alternative alleles
    output:
        directory(f"{config['working_directory']}/{config['out_name']}/temp/vep_chunks_null_annotated")
    shell:
        "mkdir -p {output}"

rule vep_other_alts:
    # Run VEP on the VCF file and output a TAB file with the annotations
    input:
        vcf=f"{config['working_directory']}/{config['out_name']}/temp/vcf_chunks_null/vcf_no_header_{{i}}_normalized_possible_alts.vcf",
        annotation=f"{config['working_directory']}/{config['out_name']}/temp/annotation.sorted.{kind}.gz",
        fasta = config["ref_genome"],
        tbi = f"{config['working_directory']}/{config['out_name']}/temp/annotation.sorted.{kind}.gz.csi",
        dir = f"{config['working_directory']}/{config['out_name']}/temp/vep_chunks_null_annotated",
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/vcf_chunks_null_annotated/vcf_no_header_{{i}}_annotated_one_per_line.txt"
    params:
        f"{config['working_directory']}/{config['out_name']}/temp/vep_chunks_null_annotated/vcf_no_header_{{i}}_annotated_one_per_line_temp.txt"
    singularity:
        "docker://ensemblorg/ensembl-vep:release_100.2"
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/vep_null/vcf_no_header_{{i}}_annotated_one_per_line.log"
    shell:
        f'vep -i {{input.vcf}} --{kind} {{input.annotation}} --fasta {{input.fasta}} -o {{params}} --force_overwrite --tab --fields "Location,REF_ALLELE,Allele,Consequence,Feature,cDNA_position,HGVSc,STRAND,CANONICAL" --hgvs --show_ref_allele --canonical 2> {{log}}   && cat {{params}} | grep -v "##" | grep -v "stream_gene_variant" | grep -v "intergenic" > {{output}}'

rule extract_spliced_sequences_generated_alts:
    # Extract the sequences flanking the SNP for the generated alternative alleles
    input:
        vcf=f"{config['working_directory']}/{config['out_name']}/temp/vcf_chunks_null_annotated/vcf_no_header_{{i}}_annotated_one_per_line.txt",
        cds_pos=f"{config['working_directory']}/{config['out_name']}/temp/cdna_pos.txt",
        cdna = f"{config['working_directory']}/{config['out_name']}/temp/cdna.fa",
        cdna_index = f"{config['working_directory']}/{config['out_name']}/temp/cdna.fa.fai",
        database=f"{config['working_directory']}/{config['out_name']}/temp/gffread_table.json",
    message:
        "Extracting the sequences flanking the SNP for the generated alternative alleles ..."
    params:
        flank=config["flank_len"],
    output:
        seqs=f"{config['working_directory']}/{config['out_name']}/temp/extracted_sequences_null/extracted_seqs_null_{{i}}.txt",
    singularity:
        "docker://kjkirven/process_seq"
    shell:
        f"python3 workflow/scripts/get_spliced_read_data.py --vcf {{input.vcf}} --ref-seqs {{input.cdna}} --flank {{params.flank}} --gffread {{input.database}} --cds-pos {{input.cds_pos}} --o {{output.seqs}}"

rule combine_extracted_sequences_generated_alts:
    # Combine the extracted sequences into one file
    input:
        expand(
            f"{config['working_directory']}/{config['out_name']}/temp/extracted_sequences_null/extracted_seqs_null_{{i}}.txt",
            i=range(1, config["chunks"] + 1)),
    message:
        "Combining the extracted sequences for the generated alternative alleles into one file ..."
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/extracted_sequences_null/extracted_seqs_null.txt"
    singularity:
        "docker://kjkirven/process_seq"
    shell:
        "cat {input} > {output}"

rule remove_duplicates_generated_alts:
    # Remove duplicates from the extracted sequences for the generated alternative alleles
    input:
        f"{config['working_directory']}/{config['out_name']}/temp/extracted_sequences_null/extracted_seqs_null.txt"
    message:    
        "Removing duplicates from the extracted sequences for the generated alternative alleles ..."
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/extracted_sequences_null/extracted_seqs_null_unique.txt"
    singularity:
        "docker://kjkirven/process_seq"
    shell:
        f"python3 workflow/scripts/remove_duplicates.py -i {{input}} -o {{output}}"

rule chunk_extracted_sequences_generated_alts:
    # Chunk the extracted sequences:
    input:
        f"{config['working_directory']}/{config['out_name']}/temp/extracted_sequences_null/extracted_seqs_null_unique.txt" 
    message:
        "Chunking the extracted sequences for the generated alternative alleles ..."
    output:
        expand(
            f"{config['working_directory']}/{config['out_name']}/temp/extracted_sequences_null/extracted_seqs_null_unique_chunk_{{i}}.txt",
            i=range(1, config["chunks"] + 1),
        ),
    singularity:
        "docker://kjkirven/process_seq"
    shell:
        f"python3 workflow/scripts/chunk_extracted_seqs.py --input {{input}} --dir {config['working_directory']}/{config['out_name']}/temp --chunk-total {config['chunks']} --null"

rule run_snpfold_generated_alts:
    # Perform the riboSNitch analysis with SNPFold for null datasets
    input:
        f"{config['working_directory']}/{config['out_name']}/temp/extracted_sequences_null/extracted_seqs_null_unique_chunk_{{i}}.txt",
    message:
        "Running SNPFold for datasets with generated alternative alleles ..."
    params:
        f"{{temp_deg}}",
    output:
        ribo=f"{config['working_directory']}/{config['out_name']}/temp/ribosnitch_chunks_null_{{temp_deg}}/chunk_{{i}}_riboSNitch_{{temp_deg}}.txt",
        error=f"{config['working_directory']}/{config['out_name']}/temp/ribosnitch_chunks_null_{{temp_deg}}/chunk_{{i}}_riboSNitch_{{temp_deg}}_error.txt",
    singularity:
        "docker://kjkirven/snpfold:latest"
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/ribosnitch_prediction_null/chunk_{{i}}_riboSNitch_{{temp_deg}}.log",
    shell:
        f"python3 workflow/scripts/snpfold_wrapper.py --i {{input[0]}} --o {{output.ribo}} --flank {config['flank_len']} --temp {{params}}"


rule combine_ribosnitch_results_generated_alts:
    # Combine the results of riboSNitch predictions for the generated alternative alleles
    input:
        [
            f"{config['working_directory']}/{config['out_name']}/temp/ribosnitch_chunks_null_{{temp_deg}}/chunk_{i}_riboSNitch_{{temp_deg}}.txt"
            for i in range(1, config["chunks"] + 1)
        ],
    message:
        "Combining the results of riboSNitch predictions for the generated alternative alleles ..."
    output:
        f"{config['working_directory']}/{config['out_name']}/results/ribosnitch_predictions_null/combined_ribosnitch_prediction_{{temp_deg}}.txt",
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/combine_ribosnitch_results_null_{{temp_deg}}.log",
    shell:
        "echo    'Chrom Pos     Transcript_pos  Ref     Alt     Flank_left      Flank_right     Gene    Match   Type    Strand  Score' > {output} && cat {input} >> {output}"