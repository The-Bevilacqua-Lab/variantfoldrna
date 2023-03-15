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
import gzip 

def prRed(skk): print("\033[91m {}\033[00m" .format(skk))

# Read in the config file
configfile: srcdir("../config.yaml")

# Check to see if the VCF file is gzipped using the magic number
with open(config['vcf_file'], 'rb') as f:
    magic_number = f.read(2)
    if magic_number == b'\x1f\x8b':
        cmd = "zcat"
    else:
        cmd = "cat"

rule get_vcf_header:
    # Get the header from the VCF file so that it can be added back in later
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/vcf_header.txt.gz",
    params:
        output = f"{config['working_directory']}/{config['out_name']}/temp/vcf_header.txt"
    shell:
        f"{cmd} < {config['vcf_file']} | grep '##' > {{params.output}} && gzip {{params.output}}"

rule rid_header:
    # Get rid of the header from the VCF file so that it is
    # not included in the chunks
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/vcf_no_header.vcf.gz",
    params:
        output = f"{config['working_directory']}/{config['out_name']}/temp/vcf_no_header.vcf"
    shell:
        f"{cmd} < {config['vcf_file']} | grep -v '##' > {{params.output}} && gzip {{params.output}}"
