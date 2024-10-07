
################################################################################
# Rules for riboSNitch prediction from CSV input 
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


rule run_snpfold_csv:
    # Perform the riboSNitch analysis with snpfold
    input:
        f"{config['tmp_dir']}/csv_chunks/csv_chunk_{{i}}.csv"
    params:
        f"{{temp_deg}}",
    output:
        ribo=f"{config['tmp_dir']}/ribosnitch_predictions_csv/chunk_{{i}}_riboSNitch_snpfold_{{temp_deg}}.txt",
    conda:
        f"{src_dir}/../variantfoldrna/workflow/envs/snpfold.yaml"
    singularity:
        "docker://condaforge/mambaforge"
    shell:
        f"python3 {src_dir}/../variantfoldrna/workflow/scripts/from_csv_snpfold.py --i {{input}} --o {{output.ribo}} --temp {{params}}"


rule combine_ribosnitch_results_snpfold:
    # Combine the results of riboSNitch prediction into one file
    input:
        [
            f"{config['tmp_dir']}/ribosnitch_predictions_csv/chunk_{i}_riboSNitch_snpfold_{{temp_deg}}.txt"
            for i in range(1, config["chunks"] + 1)
        ],
    output:
        f"{config['tmp_dir']}/ribosnitch_predictions_csv/combined_ribosnitch_prediction_snpfold_{{temp_deg}}.txt",
    log:
        f"{config['tmp_dir']}/logs/combine_ribosnitch_results_snpfold_{{temp_deg}}.log",
    shell:
        "echo    'ID	Ref	Alt	Seq	Flank	REF_dG 	REF_ED	ALT_dG	ALT_ED	snpfold_score' > {output} && cat {input} >> {output}"
    