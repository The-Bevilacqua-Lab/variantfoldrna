############################################################################################
# Rules for running the Riprap tool
#
# Author: Kobie Kirven
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
############################################################################################

import os
import sys

# Get the path to the script
script_path = os.path.realpath(__file__)
src_dir = os.path.dirname(script_path)


###########################
# Rules for running Riprap
###########################
rule run_remurna:
    # Perform the riboSNitch analysis with Riprap
    input:
        f"{config['tmp_dir']}/extracted_seqs_chunks/extracted_flank_snp_{{i}}.txt",
    params:
        f"{{temp_deg}}",
    output:
        ribo=f"{config['tmp_dir']}/ribosnitch_chunks_{{temp_deg}}/chunk_{{i}}_riboSNitch_remurna_{{temp_deg}}.txt",
        error=f"{config['tmp_dir']}/ribosnitch_chunks_{{temp_deg}}/chunk_{{i}}_riboSNitch_remurna_{{temp_deg}}_error.txt",
    conda:
        f"{src_dir}/../variantfoldrna/workflow/envs/remurna.yaml"
    singularity:
        "docker://condaforge/mambaforge"
    log:
        f"{config['tmp_dir']}/logs/ribosnitch_prediction/chunk_{{i}}_riboSNitch_remurna_{{temp_deg}}.log",
    shell:
        f"python3 {src_dir}/../variantfoldrna/workflow/scripts/remurna_wrapper.py --i {{input}} --o {{output.ribo}} --temp {{params}} --flank {config['flank_len']}"


rule combine_ribosnitch_results_remurna:
    # Combine the results of riboSNitch prediction into one file
    input:
        [
            f"{config['tmp_dir']}/ribosnitch_chunks_{{temp_deg}}/chunk_{i}_riboSNitch_remurna_{{temp_deg}}.txt"
            for i in range(1, config["chunks"] + 1)
        ],
    output:
        f"{config['tmp_dir']}/ribosnitch_predictions/combined_ribosnitch_prediction_remurna_{{temp_deg}}.txt",
    log:
        f"{config['tmp_dir']}/logs/combine_ribosnitch_results_remurna_{{temp_deg}}.log",
    shell:
        "echo    'Chrom	Pos	Transcript_pos	Ref	Alt	Flank_left	Flank_right	Gene	Match	Type	Strand	remuRNA_score' > {output} && cat {input} >> {output}"