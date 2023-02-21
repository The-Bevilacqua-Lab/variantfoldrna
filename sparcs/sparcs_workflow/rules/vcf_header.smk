################################################################################
# Rules for getting rid of and collecting the header from the VCF file
#
# Author: Kobie Kirven
#
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
################################################################################

# Read in the config file
configfile: srcdir("../config.yaml")

# Check if the VCF file is gzipped
if config['vcf_file'].endswith(".gz"):
    # If the VCF file is gzipped, use zcat to get rid of the header
    cmd = "gzcat"
else:
    # If the VCF file is not gzipped, use cat to get rid of the header
    cmd = "cat"

rule rid_header:
    # Get rid of the header from the VCF file so that it is
    # not included in the chunks
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/vcf_no_header.vcf.gz",
    params:
        output = f"{config['working_directory']}/{config['out_name']}/temp/vcf_no_header.vcf"
    shell:
        f"{cmd} {config['vcf_file']} | grep -v '##' > {{params.output}} && gzip {{params.output}}"


rule get_vcf_header:
    # Get the header from the VCF file so that it can be added back in later
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/vcf_header.txt.gz",
    params:
        output = f"{config['working_directory']}/{config['out_name']}/temp/vcf_header.txt"
    shell:
        f"{cmd} {config['vcf_file']} | grep '##' > {{params.output}} && gzip {{params.output}}"
