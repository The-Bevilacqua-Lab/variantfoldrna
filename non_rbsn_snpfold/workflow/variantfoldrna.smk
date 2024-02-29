################################################################################
# VariantFoldRNA: A Snakemake Pipeline for RiboSNitch Prediction
#
# Author: Kobie Kirven
# Email: kjk6173@psu.edu
#
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
################################################################################

# Import the python modules:
import os
import subprocess


# -- funcitons -- #
def prCyan(skk):
    """
    Print in cyan
    """
    print("\033[96m {}\033[00m".format(skk))


# Get the location of this file:
location = os.getcwd()

# Get the path up to the VariantFoldRNA directory:
path = []
for ele in location.split("/"):
    if ele == "variantfoldrna":
        path.append(ele)
        break
    else:
        path.append(ele)

# Convert the path to a string:
path = "/".join(path)


# Config File
configfile: srcdir("config.yaml")


# -- Import common rules -- #
if config['from_csv'] == False:
    include: "rules/chunk.smk"
    include: "rules/vep.smk"
    # include: "rules/plot.smk"
    include: "rules/vcf_header.smk"
    # include: "rules/get_top_percent.smk"
    include: "rules/neutral_background.smk"

# Load the rules for the appropriate prediction tool
if config["ribosnitch_prediction_tool"].lower() == "snpfold":

    include: "rules/snpfold.smk"

elif config["ribosnitch_prediction_tool"].lower() == "riprap":

    include: "rules/riprap.smk"

elif config["ribosnitch_prediction_tool"].lower() == "rnasnp:p-value" or config["ribosnitch_prediction_tool"].lower() == "rnasnp:dist":

    include: "rules/rnasnp.smk"

elif config["ribosnitch_prediction_tool"].lower() == "remurna":

    include: "rules/remurna.smk"

elif config["ribosnitch_prediction_tool"].lower() == "delta_ensemble_diversity" or config["ribosnitch_prediction_tool"].lower() == "delta_ensemble_free_energy":

    include: "rules/ensemble.smk"

    
########################################################
# If the user would like the spliced cDNA, include the
# appropriate rules
########################################################

if config["spliced"] == True:

    include: "rules/extract_seqs_spliced.smk"

else:

    include: "rules/extract_seqs.smk"


###########################################################
# If the user would like to perform riboSNitch prediction
# over a range of temperatures, adjust the output
# accordingly
###########################################################
if "@" in str(config["temperature"]):
    start_stop = str(config["temperature"]).split("@")
    temperature_range = range(
        int(start_stop[0]), int(start_stop[1]) + 1, int(config["temp_step"])
    )
else:
    temperature_range = [config["temperature"]]

#############################################
# Create the final input list
#############################################
final_input = []

if config['from_csv'] != "NA":
    for temp in temperature_range:
        final_input.append(f"{config['working_directory']}/{config['out_name']}/results/ribosnitch_predictions_csv/combined_ribosnitch_prediction_{temp}.txt")

elif config['null_seqs_only'] == False:
    for temp in temperature_range:
        # If the user just wants the riboSNitch predictions without the null predictions
        if config["rbsn_only"] == True:
            final_input.append(
                f"{config['working_directory']}/{config['out_name']}/results/ribosnitch_predictions/combined_ribosnitch_prediction_{temp}.txt"
            )

        # If the user just wants the null predictions without the riboSNitch predictions for the natural variants
        elif config["null_only"] == True:
            final_input.append(
                f"{config['working_directory']}/{config['out_name']}/results/null_model/combined_ribosnitch_prediction_null_{temp}.txt"
            )

        elif conig['other_alts_only'] == True:
            final_input.append(
                f"{config['working_directory']}/{config['out_name']}/results/ribosnitch_predictions_other_alts/combined_ribosnitch_prediction_{temp}.txt"
            )

        # If the user wants both the riboSNitch predictions and the null predictions
        else:
            final_input.append(
                f"{config['working_directory']}/{config['out_name']}/results/ribosnitch_predictions/combined_ribosnitch_prediction_{temp}.txt"
            )
            final_input.append(
                f"{config['working_directory']}/{config['out_name']}/results/ribosnitch_predictions_null/combined_ribosnitch_prediction_{temp}.txt"
            )

else:
    final_input = [f"{config['working_directory']}/{config['out_name']}/temp/intergenic_flank_seq.txt"]

# Let the user know what files we are creating
prCyan("Creating the following files:")
prCyan("\t-" + "\n\t-".join(final_input))


#######################
#  --  Pipeline  --   #
#######################

rule all:
    input:
        final_input,
