################################################################################
# Rules for getting rid of and collecting the header from the VCF file
#
# Author: Kobie Kirven
#
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
################################################################################

# imports 
import sys

def prRed(skk): print("\033[91m {}\033[00m" .format(skk))

# Read in the config file
configfile: srcdir("../config.yaml")

# Check if the VCF file is gzipped
if config['vcf_file'].endswith(".gz"):
    # If the VCF file is gzipped, use zcat to get rid of the header
    cmd = "gzcat"
else:
    # If the VCF file is not gzipped, use cat to get rid of the header
    cmd = "cat"

rule validate_vcf:
    # Validate the VCF file
    input:
        f"{config['working_directory']}/{config['out_name']}/temp/vcf_no_header.vcf.gz"
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/vcf_check.txt"
    conda:
        "../envs/process_seq.yaml"
    shell:
        "python3 workflow/scripts/validate_vcf.py -i {input} >> {output}"

rule vcf_validation_results:
    # Let us know the results of the VCF validation
    input:
        f"{config['working_directory']}/{config['out_name']}/temp/vcf_check.txt"
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/vcf_validation_results.txt"
    run:
        with open(input[0], "r") as f:
            for line in f:
                if line.startswith("Error"):
                    prRed("Error: VCF file does not appear to be valid. Please check the VCF file and try again.")
                    sys.exit(1)
                else:
                    with open(output[0], "w") as o:
                        o.write("VCF file is valid.")

rule get_vcf_header:
    # Get the header from the VCF file so that it can be added back in later
    input:
        check = f"{config['working_directory']}/{config['out_name']}/temp/vcf_validation_results.txt"
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/vcf_header.txt.gz",
    params:
        output = f"{config['working_directory']}/{config['out_name']}/temp/vcf_header.txt"
    shell:
        f"{cmd} {config['vcf_file']} | grep '##' > {{params.output}} && gzip {{params.output}}"

rule rid_header:
    # Get rid of the header from the VCF file so that it is
    # not included in the chunks
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/vcf_no_header.vcf.gz",
    params:
        output = f"{config['working_directory']}/{config['out_name']}/temp/vcf_no_header.vcf"
    shell:
        f"{cmd} {config['vcf_file']} | grep -v '##' > {{params.output}} && gzip {{params.output}}"
