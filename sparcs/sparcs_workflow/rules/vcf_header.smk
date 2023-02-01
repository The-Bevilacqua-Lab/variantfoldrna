################################################################################
# Rules for getting rid of and collecting the header from the VCF file
#
# Author: Kobie Kirven
#
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
################################################################################
configfile: srcdir("../config.yaml")


rule rid_header:
    # Get rid of the header from the VCF file so that it is
    # not included in the chunks
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/vcf_no_header.vcf",
    shell:
        f"cat {config['vcf_file']} | grep -v '##' > {{output}}"


rule get_vcf_header:
    # Get the header from the VCF file so that it can be added back in later
    output:
        f"{config['working_directory']}/{config['out_name']}/temp/vcf_header.txt",
    shell:
        f"cat {config['vcf_file']} | grep '##' > {{output}}"
