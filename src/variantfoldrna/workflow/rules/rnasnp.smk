################################################################################
# Rules for riboSNitch prediction
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


rule run_rnasnp:
    # Perform the riboSNitch analysis with Riprap
    input:
        f"{config['tmp_dir']}/extracted_seqs_chunks/extracted_flank_snp_{{i}}.txt",
    params:
        f"{{temp_deg}}",
    output:
        ribo=f"{config['tmp_dir']}/ribosnitch_chunks_{{temp_deg}}/chunk_{{i}}_riboSNitch_{{temp_deg}}.txt",
        error=f"{config['tmp_dir']}/ribosnitch_chunks_{{temp_deg}}/chunk_{{i}}_riboSNitch_{{temp_deg}}_error.txt",
    conda:
        f"{src_dir}/../variantfoldrna/workflow/envs/rnasnp.yaml"
    singularity:
        "docker://condaforge/mambaforge"
    log:
        f"{config['tmp_dir']}/logs/ribosnitch_prediction/chunk_{{i}}_riboSNitch_{{temp_deg}}.log",
    shell:
        f"python3 {src_dir}/../variantfoldrna/workflow/scripts/rnasnp_wrapper.py --i {{input}} --o {{output.ribo}} --flank {config['flank_len']} --kind {config['ribosnitch_prediction_tool'].lower().split(':')[1]}"


rule combine_ribosnitch_results:
    # Combine the results of riboSNitch prediction into one file
    input:
        [
            f"{config['tmp_dir']}/ribosnitch_chunks_{{temp_deg}}/chunk_{i}_riboSNitch_{{temp_deg}}.txt"
            for i in range(1, config["chunks"] + 1)
        ],
    output:
        f"{config['out_dir']}/ribosnitch_predictions/combined_ribosnitch_prediction_{{temp_deg}}.txt",
    log:
        f"{config['out_dir']}/logs/combine_ribosnitch_results_{{temp_deg}}.log",
    shell:
        "Chrom	Pos	Transcript_pos	Ref	Alt	Flank_left	Flank_right	Gene	Match	Type	Strand	RNAsnp_score' > {output} && cat {input} >> {output}"


rule run_rnasnp_csv:
    # Perform the riboSNitch analysis with Riprap
    input:
        f"{config['csv']}",
    params:
        f"{{temp_deg}}",
    output:
        ribo=f"{config['out_dir']}/ribosnitch_predictions_csv/combined_ribosnitch_prediction_{{temp_deg}}.txt",
    conda:
        f"{src_dir}/../variantfoldrna/workflow/envs/rnasnp.yaml"
    singularity:
        "docker://condaforge/mambaforge"
    shell:
        f"python3 {src_dir}/../variantfoldrna/workflow/scripts/csv_rnasnp.py --i {{input}} --o {{output.ribo}} --flank {config['flank_len']} --kind {config['ribosnitch_prediction_tool'].lower().split(':')[1]}"
