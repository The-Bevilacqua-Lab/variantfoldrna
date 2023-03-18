################################################################################
# Rules for riboSNitch prediction
#
# Author: Kobie Kirven
#
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
################################################################################
configfile: srcdir("../config.yaml")


# Import the python modules:
import os


rule run_snpfold:
    # Perform the riboSNitch analysis with SNPFold
    input:
        f"{config['working_directory']}/{config['out_name']}/temp/extracted_seqs_chunks/extracted_flank_snp_{{i}}.txt",
    params:
        f"{{temp_deg}}",
    output:
        ribo=f"{config['working_directory']}/{config['out_name']}/temp/ribosnitch_chunks_{{temp_deg}}/chunk_{{i}}_riboSNitch_{{temp_deg}}.txt",
        error=f"{config['working_directory']}/{config['out_name']}/temp/ribosnitch_chunks_{{temp_deg}}/chunk_{{i}}_riboSNitch_{{temp_deg}}_error.txt",
    conda:
        "../envs/snpfold.yaml"
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/ribosnitch_prediction/chunk_{{i}}_riboSNitch_{{temp_deg}}.log",
    shell:
        f"python3 workflow/scripts/snpfold_wrapper.py --i {{input[0]}} --o {{output.ribo}} --flank {config['flank_len']} --temp {{params}}"


rule combine_ribosnitch_results:
    # Combine the results of riboSNitch prediction into one file
    input:
        [
            f"{config['working_directory']}/{config['out_name']}/temp/ribosnitch_chunks_{{temp_deg}}/chunk_{i}_riboSNitch_{{temp_deg}}.txt"
            for i in range(1, config["chunks"] + 1)
        ],
    output:
        f"{config['working_directory']}/{config['out_name']}/results/ribosnitch_predictions/combined_ribosnitch_prediction_{{temp_deg}}.txt",
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/combine_ribosnitch_results_{{temp_deg}}.log",
    shell:
        "echo    'Chrom    Pos    Ref    Alt    Flank_left    Flank_right    Gene    Match    Type    Strand    Effect    Score' > {output}  && cat {input} >> {output}"


# rule combine_ribosnitch_errors:
#     # Combine the errors from riboSNitch prediction into one file
#     input:
#         expand(f"{config['working_directory']}/{config['out_name']}/temp/ribosnitch_chunks_{{temp_deg}}/chunk_{{i}}_riboSNitch_{{temp_deg}}_error.txt", i=range(1,config["chunks"]+1), temp_deg=wildcards.temp_deg)
#     output:
#         f"{config['working_directory']}/{config['out_name']}/results/ribosnitch_prediction/errors/combined_ribosnitch_prediction_error_{{temp_deg}}.txt"
#     shell:
#         "cat {input} > {output}"
