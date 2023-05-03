################################################################################
# Rules for riboSNitch prediction
#
# Author: Kobie Kirven
#
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
################################################################################

rule run_rnasnp:
    # Perform the riboSNitch analysis with Riprap
    input:
        f"{config['working_directory']}/{config['out_name']}/temp/extracted_seqs_chunks/extracted_flank_snp_{{i}}.txt",
    params:
        f"{{temp_deg}}",
    output:
        ribo=f"{config['working_directory']}/{config['out_name']}/temp/ribosnitch_chunks_{{temp_deg}}/chunk_{{i}}_riboSNitch_{{temp_deg}}.txt",
        error=f"{config['working_directory']}/{config['out_name']}/temp/ribosnitch_chunks_{{temp_deg}}/chunk_{{i}}_riboSNitch_{{temp_deg}}_error.txt",
    conda:
        "../envs/rnasnp.yaml"
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/ribosnitch_prediction/chunk_{{i}}_riboSNitch_{{temp_deg}}.log",
    shell:
        f"python3 scripts/rnasnp_wrapper.py --i {{input}} --o {{output.ribo}} --flank {config['flank_len']} --kind {config['ribosnitch_prediction_tool'].lower().split(':')[1]}"

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
        "echo    'Chrom	Pos	Ref	Alt	Flank_left	Flank_right	Gene	Match	Type	Strand	Effect	Score' > {output} && cat {input} >> {output}"
