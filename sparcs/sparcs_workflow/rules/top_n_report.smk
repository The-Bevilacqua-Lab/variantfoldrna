##############################################
# Rules for creating the HTML report 
##############################################

rule get_top_n_percent:
    # Return the top n-percent of SNPs with the highest riboSNitch score
    input:
        f"{config['working_directory']}/{config['out_name']}/results/ribosnitch_predictions/combined_ribosnitch_prediction_{{temp_deg}}.txt",
    output:
        f"{config['working_directory']}/{config['out_name']}/results/ribosnitch_predictions/combined_ribosnitch_prediction_top_{config['top_n_percent']}_{temp}.txt"
    shell:
        f"sort -k 12 -nr {{input}} |  head -n $(($(wc -l < {{input}}) * {config['top_n_percent']} / 100)) {{input}} > {{output}}"

rule get_secondary_structure_and_pss:
    input:
        f"{config['working_directory']}/{config['out_name']}/results/ribosnitch_predictions/combined_ribosnitch_prediction_top_{config['top_n_percent']}_{temp}.txt"
    output:
        f"{config['working_directory']}/{config['out_name']}/results/ribosnitch_predictions/combined_ribosnitch_prediction_top_{config['top_n_percent']}_{temp}_with_secondary_structure.txt",
    singularity:
        "docker://kjkirven/snpfold:latest"
    shell:
        f"python3 {config['scripts_directory']}/get_secondary_structure_and_pss.py {{input}} {{output}}"

