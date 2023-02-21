##############################################################################
# Validate that a VCF file is valid
#
##############################################################################

import argparse 
import sys
import subprocess

def validate_vcf(file_name, gzip_file=False):
    """
    Validate the VCF file
    """
    if gzip_file:
        cmd = 'gzcat'
    else:
        cmd = 'cat'
    cmd = f"{cmd} {file_name} | head -n 300 | vcf-validator"
    try:
        subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        print("Valid")
    except:
        print("Error")

def main():
    # -- Parse the command line arguments -- #
    parser = argparse.ArgumentParser(description="Validate a VCF file")
    parser.add_argument("-i", "--input", help="VCF file to validate", required=True)
    args = parser.parse_args()

    # Check to see if we are dealing with a gzipped VCF file or not
    if args.input.endswith(".gz"):
        vcf_gz = True
    else:
        vcf_gz = False

    # Validate the VCF file
    validate_vcf(args.input, gzip_file=vcf_gz)

if __name__ == "__main__":
    main()
