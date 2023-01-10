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

link = "https://github.com/ouyang-lab/Riprap/raw/master/script.zip"

rule download_riprap:
    # Download the riprap riboSNitch prediction tool
    output:
        f"{path}/workflow/scripts/riprap.py"
    conda:
        "../envs/general.yaml"
    shell:
        f"wget {link} -O {path}/workflow/scripts/riprap.zip && unzip {path}/workflow/scripts/riprap.zip -d {path}/workflow/scripts/ && rm {path}/workflow/scripts/riprap.zip && mv {path}/workflow/scripts/Riprap_software_1.0.py {path}/workflow/scripts/riprap.py"
