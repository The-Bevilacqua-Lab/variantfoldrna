####################################################################################################
# Rules for plotting various results
#
# Author: Kobie Kirven
# Assmann and Bevilacqua Labs
####################################################################################################

# Read in the config file:
configfile: srcdir("../config.yaml")

# Import the python modules:
import os


rule plot_scores:
    # Plot the results of the riboSNtch prediciton
    input:
        f"{config['working_directory']}/{config['out_name']}/results/ribosnitch_predictions/combined_ribosnitch_prediction_{{temp_deg}}.txt",
    output:
        f"{config['working_directory']}/{config['out_name']}/results/ribosnitch_predictions/combined_ribosnitch_prediction_hist_{{temp_deg}}.png",
    singularity:
        "docker://kjkirven/process_seq"
    shell:
        f"python3 scripts/plot_scores.py --i {{input}} --o {{output}} --t {config['ribosnitch_prediction_tool']}"
