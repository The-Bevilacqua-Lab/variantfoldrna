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


rule run_snpfold:
    # Perform the riboSNitch analysis with SNPFold
    input:
        f"{config['tmp_dir']}/extracted_seqs_chunks/extracted_flank_snp_{{i}}.txt",
    params:
        f"{{temp_deg}}",
    output:
        ribo=f"{config['tmp_dir']}/ribosnitch_chunks_{{temp_deg}}/chunk_{{i}}_riboSNitch_snpfold_{{temp_deg}}.txt",
        error=f"{config['tmp_dir']}/ribosnitch_chunks_{{temp_deg}}/chunk_{{i}}_riboSNitch_snpfold_{{temp_deg}}_error.txt",
    conda:
        f"{src_dir}/../variantfoldrna/workflow/envs/snpfold.yaml"
    singularity:
        "docker://condaforge/mambaforge"
    log:
        f"{config['tmp_dir']}/logs/ribosnitch_prediction/chunk_{{i}}_riboSNitch_snpfold_{{temp_deg}}.log",
    shell:
        f"python3 {src_dir}/../variantfoldrna/workflow/scripts/snpfold_wrapper.py --i {{input[0]}} --o {{output.ribo}} --flank {config['flank_len']} --temp {{params}}"


rule combine_ribosnitch_results_snpfold:
    # Combine the results of riboSNitch prediction into one file
    input:
        [f"{config['tmp_dir']}/ribosnitch_chunks_{{temp_deg}}/chunk_{i}_riboSNitch_snpfold_{{temp_deg}}.txt" for i in range(1, config["chunks"] + 1)],
    output:
        f"{config['tmp_dir']}/ribosnitch_predictions/combined_ribosnitch_prediction_snpfold_{{temp_deg}}.txt",
    log:
        f"{config['tmp_dir']}/logs/combine_ribosnitch_results_snpfold_{{temp_deg}}.log",
    shell:
        "echo    'Chrom	Pos	Transcript_pos	Ref	Alt	Flank_left	Flank_right	Gene	Match	Type	Strand	Ref_dG	Ref_ED	Alt_dG	Alt_ED	SNPfold_score' > {output} && cat {input} | grep -v 'NO_MATCH' | grep '.' | grep -v '>' >> {output}"



# rule combine_ribosnitch_results_csv:
#     # Combine the results of riboSNitch prediction into one file
#     input:
#         [
#             f"{config['out_dir']}/ribosnitch_chunks_{{temp_deg}}/chunk_{i}_riboSNitch_{{temp_deg}}.txt"
#             for i in range(1, config["chunks"] + 1)
#         ],
#     output:
#         f"{config['out_dir']}/ribosnitch_predictions/combined_ribosnitch_prediction_{{temp_deg}}.txt",
#     log:
#         f"{config['out_dir']}/logs/combine_ribosnitch_results_{{temp_deg}}.log",
#     shell:
#         "echo    'Chrom	Pos	Transcript_pos	Ref	Alt	Flank_left	Flank_right	Gene	Match	Type	Strand	Ref_dG	Alt_dG	Ref_ED	Alt_ED	Score' > {output} && cat {input} >> {output}"
# rule combine_ribosnitch_errors:
#     # Combine the errors from riboSNitch prediction into one file
#     input:
#         expand(f"{config['out_dir']}/ribosnitch_chunks_{{temp_deg}}/chunk_{{i}}_riboSNitch_{{temp_deg}}_error.txt", i=range(1,config["chunks"]+1), temp_deg=wildcards.temp_deg)
#     output:
#         f"{config['out_dir']}/ribosnitch_prediction/errors/combined_ribosnitch_prediction_error_{{temp_deg}}.txt"
#     shell:
#         "cat {input} | grep -v 'NO' | grep '-' | grep -v '>' > {output}"