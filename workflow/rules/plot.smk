####################################################################################################
# Rules for plotting various results
#
# Author: Kobie Kirven
# Assmann and Bevilacqua Labs
####################################################################################################

# Import the python modules:
import os

# Get the location of this file:
location = os.getcwd()

# Get the path up to the SPARCS directory:
path = []
for ele in location.split("/"):
    if ele == "SPARCS":
        path.append(ele)
        break
    else:
        path.append(ele)

# Convert the path to a string:
path = "/".join(path)


rule plot_snpfold:
    # Plot the results of the riboSNtch prediciton
    input:
        f"{config['working_directory']}/{config['out_name']}/results/ribosnitch_predictions/combined_ribosnitch_prediction_{{temp_deg}}.txt",
    output:
        f"{config['working_directory']}/{config['out_name']}/results/ribosnitch_predictions/snpfold_scores_hist_t{{temp_deg}}.jpg",
    conda:
        "../envs/plotting.yaml"
    shell:
        f"python3 {path}/workflow/scripts/plot_snpfold.py --i {{input}} --o {{output}}"


rule plot_indelfold:
    input:
        f"{config['working_directory']}/{config['out_name']}/results/indelfold_predictions/combined_indelfold_prediction_t{{temp_deg}}.txt",
    output:
        f"{config['working_directory']}/{config['out_name']}/results/indelfold_predictions/indelfold_scores_hist_t{{temp_deg}}.jpg",
    conda:
        "../envs/plotting.yaml"
    shell:
        f"python3 {path}/workflow/scripts/plot_indelfold.py --i {{input}} --o {{output}}"
