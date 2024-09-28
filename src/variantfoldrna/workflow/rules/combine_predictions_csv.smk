script_path = os.path.realpath(__file__)
src_dir = os.path.dirname(script_path)

rule combine_ribosnitch_results_total:
    # Combine the results of riboSNitch prediction into one file
    input:
        [f"{config['tmp_dir']}/ribosnitch_predictions_csv/combined_ribosnitch_prediction_{tool}_{{temp_deg}}.txt" 
         for tool in config["ribosnitch_prediction_tool"].lower().split(",")]
    output:
        f"{config['out_dir']}/ribosnitch_predictions_csv/combined_ribosnitch_prediction_{{temp_deg}}.txt"
    params:
        " ".join([f"{config['tmp_dir']}/ribosnitch_predictions_csv/combined_ribosnitch_prediction_{tool}_{{temp_deg}}.txt" 
         for tool in config["ribosnitch_prediction_tool"].lower().split(",")])
    shell:
        f"python3 {src_dir}/../variantfoldrna/workflow/scripts/combine_results.py {{params}} {{output}}"