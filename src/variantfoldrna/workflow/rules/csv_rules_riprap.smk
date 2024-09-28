
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

rule run_riprap_csv:
    # Perform the riboSNitch analysis with Riprap
    input:
        f"{config['csv']}",
    params:
        f"{{temp_deg}}",
    output:
        ribo=f"{config['tmp_dir']}/ribosnitch_predictions_csv/combined_ribosnitch_prediction_riprap_{{temp_deg}}.txt",
    singularity:
        "docker://condaforge/mambaforge"
    conda:
        f"{src_dir}/../variantfoldrna/workflow/envs/riprap.yaml"
    shell:
        f"python3 {src_dir}/../variantfoldrna/workflow/scripts/from_csv_riprap.py --i {{input}} --o {{output.ribo}} --flank {config['flank_len']} --temp {{params}}"