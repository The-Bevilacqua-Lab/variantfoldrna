#####################################################################
# Given the output from the riboSNitch prediction, this script will
# return the top n-percent of SNPs with the highest riboSNitch score
# 
# Author: Kobie Kirven
#####################################################################

# Path to the config file
configfile: srcdir("../config.yaml")

rule get_top_n_percent:
    # Return the top n-percent of SNPs with the highest riboSNitch score
    input:
        f"{config['working_directory']}/{config['out_name']}/results/ribosnitch_predictions/combined_ribosnitch_prediction_{{temp_deg}}.txt",
    output:
        f"{config['working_directory']}/{config['out_name']}/results/ribosnitch_predictions/top_{config['top_n_percent']}_percent_{{temp_deg}}.txt"
    shell:
        f"python3 workflow/scripts/get_top_n_percent.py --input {{input}} --output {{output}} --top-n-percent {config['top_n_percent']}"

