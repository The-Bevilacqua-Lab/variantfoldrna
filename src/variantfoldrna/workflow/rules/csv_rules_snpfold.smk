
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
    # Perform the riboSNitch analysis with SNPFold
    input:
        f"{config['csv']}",
    params:
        f"{{temp_deg}}",
    output:
        ribo=f"{config['tmp_dir']}/ribosnitch_predictions_csv/combined_ribosnitch_prediction_snpfold_{{temp_deg}}.txt",
    conda:
        f"{src_dir}/../variantfoldrna/workflow/envs/snpfold.yaml"
    singularity:
        "docker://condaforge/mambaforge"
    # log:
    #     f"{config['out_dir']}/logs/ribosnitch_prediction/chunk_{{i}}_riboSNitch_{{temp_deg}}.log",
    shell:
        f"python3 {src_dir}/../variantfoldrna/workflow/scripts/from_csv_snpfold.py --i {{input[0]}} --o {{output.ribo}} --temp {{params}}"