################################################################################
# Rules for getting rid of and collecting the header from the VCF file
#
# Author: Kobie Kirven
#
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
################################################################################

# Imports
import os
import sys
import gzip

# Get the path to the script
script_path = os.path.realpath(__file__)
src_dir = os.path.dirname(script_path)


def prRed(skk):
    print("\033[91m {}\033[00m".format(skk))


# Check to see if the VCF file is gzipped using the magic number
with open(config["vcf"], "rb") as f:
    magic_number = f.read(2)
    if magic_number == b"\x1f\x8b":
        cmd = "zcat"
    else:
        cmd = "cat"


rule get_vcf_header:
    # Get the header from the VCF file so that it can be added back in later
    output:
        f"{config['tmp_dir']}/vcf_header.txt.gz",
    params:
        output=f"{config['tmp_dir']}/vcf_header.txt",
    shell:
        f"{cmd} < {config['vcf']} | grep '##' > {{params.output}} && gzip {{params.output}}"

if str(config['chromosome']).lower() != 'none':
    cmd1 = "| grep " + " | grep ".join([x for x in str(config['chromosome']).split(",")])
else:
    cmd1 = ""

rule rid_header:
    # Get rid of the header from the VCF file so that it is
    # not included in the chunks
    output:
        f"{config['tmp_dir']}/vcf_no_header.vcf.gz",
    params:
        output=f"{config['tmp_dir']}/vcf_no_header.vcf",
    shell:
        f"{cmd} < {config['vcf']} | grep -v '##' {cmd1} > {{params.output}} && gzip {{params.output}}"
