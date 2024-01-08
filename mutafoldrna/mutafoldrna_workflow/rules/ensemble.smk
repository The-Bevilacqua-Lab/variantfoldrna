# Figure out what output we want
if config['ribosnitch_prediction_tool'].lower() == "delta_ensemble_diversity":
    ribosnitch_prediction_tool = "delta_ensemble_diversity"

elif config['ribosnitch_prediction_tool'].lower() == "delta_ensemble_free_energy":
    ribosnitch_prediction_tool = "delta_ensemble_free_energy"

rule run_get_ensemble_properties:
    # Perform the riboSNitch analysis with Riprap
    input:
        f"{config['working_directory']}/{config['out_name']}/temp/extracted_seqs_chunks/extracted_flank_snp_{{i}}.txt",
    params:
        f"{{temp_deg}}",
    output:
        ribo=f"{config['working_directory']}/{config['out_name']}/temp/ribosnitch_chunks_{{temp_deg}}/chunk_{{i}}_riboSNitch_{{temp_deg}}.txt",
        error=f"{config['working_directory']}/{config['out_name']}/temp/ribosnitch_chunks_{{temp_deg}}/chunk_{{i}}_riboSNitch_{{temp_deg}}_error.txt",
    # conda:
    #     "../envs/rnasnp.yaml"
    singularity:
        "docker://kjkirven/snpfold"
    log:
        f"{config['working_directory']}/{config['out_name']}/logs/ribosnitch_prediction/chunk_{{i}}_riboSNitch_{{temp_deg}}.log",
    shell:
        f"python3 workflow/scripts/delta_ensemble_stats.py --i {{input}} --o {{output.ribo}} --temp {{params}} --tool-type {{ribosnitch_prediction_tool}}"

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