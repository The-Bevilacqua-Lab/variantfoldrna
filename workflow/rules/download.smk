############################################################
# Rules for downloading software that is not avaliable via 
# conda or pip
#
# Author: Kobie Kirven
# Assmann and Bevilacqua Labs
# The Pennsylvania State University 
############################################################

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

link = "http://rna.urmc.rochester.edu/Releases/current/RNAstructureSource.tgz"

rule download_rnastructure_datatables:
    output:
        f"{path}/scripts/data_tables/autodetect.txt"
    conda:
        "../envs/general.yaml"
    shell:
        f"(wget {link} -O {path}/scripts/rnastructure.tgz > /dev/null 2>&1) && (tar -xvzf {path}/scripts/rnastructure.tgz -C {path}/scripts/ > /dev/null 2>&1) && rm {path}/scripts/rnastructure.tgz && mv {path}/scripts/RNAstructure/data_tables/autodetect.txt {path}/scripts/data_tables/ && rm -rf {path}/scripts/RNAstructure/"

