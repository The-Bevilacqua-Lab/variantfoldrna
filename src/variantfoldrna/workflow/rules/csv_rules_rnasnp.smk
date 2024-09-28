
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


rule run_rnasnp_p_value_csv:
    # Perform the riboSNitch analysis with Riprap
    input:
        f"{config['csv']}",
    params:
        f"{{temp_deg}}",
    output:
        ribo=f"{config['tmp_dir']}/ribosnitch_predictions_csv/combined_ribosnitch_prediction_rnasnp:p-value_{{temp_deg}}.txt",
    conda:
        f"{src_dir}/../variantfoldrna/workflow/envs/rnasnp.yaml"
    singularity:
        "docker://condaforge/mambaforge"
    shell:
        f"python3 {src_dir}/../variantfoldrna/workflow/scripts/from_csv_rnasnp.py --i {{input}} --o {{output.ribo}} --flank {config['flank_len']} --kind {config['ribosnitch_prediction_tool'].lower().split(':')[1]}"


rule run_rnasnp_dist_csv:
    # Perform the riboSNitch analysis with Riprap
    input:
        f"{config['csv']}",
    params:
        f"{{temp_deg}}",
    output:
        ribo=f"{config['tmp_dir']}/ribosnitch_predictions_csv/combined_ribosnitch_prediction_rnasnp:dist_{{temp_deg}}.txt",
    conda:
        f"{src_dir}/../variantfoldrna/workflow/envs/rnasnp.yaml"
    singularity:
        "docker://condaforge/mambaforge"
    shell:
        f"python3 {src_dir}/../variantfoldrna/workflow/scripts/from_csv_rnasnp.py --i {{input}} --o {{output.ribo}} --flank {config['flank_len']} --kind {config['ribosnitch_prediction_tool'].lower().split(':')[1]}"