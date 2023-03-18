################################################################################
# SPARCS: A Snakemake Pipeline for RiboSNitch Prediction
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


# Config File
configfile: srcdir("config.yaml")


# Import Rules
include: "rules/chunk.smk"
include: "rules/snpeff.smk"
include: "rules/extract_seqs.smk"
include: "rules/plot.smk"
include: "rules/vcf_header.smk"


# Load the rules for the appropriate prediction tool
if config["ribosnitch_prediction_tool"] == "SNPfold":

    include: "rules/snpfold.smk"

elif config["ribosnitch_prediction_tool"] == "Riprap":

    include: "rules/riprap.smk"


def prCyan(skk):
    """
    Print in cyan
    """
    print("\033[96m {}\033[00m".format(skk))


if "-" in str(config["temperature"]):
    start_stop = str(config["temperature"]).split("-")
    temperature_range = range(int(start_stop[0]), int(start_stop[1]) + 1)
else:
    temperature_range = [config["temperature"]]

final_input = []
for temp in temperature_range:
    final_input.append(
        f"{config['working_directory']}/{config['out_name']}/results/ribosnitch_predictions/combined_ribosnitch_prediction_{temp}.txt"
    )
    final_input.append(
        f"{config['working_directory']}/{config['out_name']}/results/ribosnitch_predictions/combined_ribosnitch_prediction_hist_{temp}.png"
    )

# Let the user know what files we are creating
prCyan("Creating the following files:")
prCyan("\t-" + "\n\t-".join(final_input))


#######################
#  --  Pipeline  --   #
#######################
rule all:
    input:
        final_input,
