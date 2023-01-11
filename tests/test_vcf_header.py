##############################################################################
# This script will test all of the rules in the vcf_header.smk file
#
# Author: Kobie Kirven
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
##############################################################################

# Imports
import os
import sys
import subprocess
import unittest
from utils import run_snakemake


def prCyan(skk):
    print("\033[96m {}\033[00m".format(skk))


# Get the path to the SPARCS directory
workflow_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
workflow_path = "/".join(workflow_path.split("/")[:-1])


#######################################
#  --  Test the snakemake pipeline  --#
#######################################
class TestPipeline(unittest.TestCase):
    def test_vcf_header(self):

        # Let the oberver know that we are testing the vcf_header rule
        prCyan("Currently testing: rule vcf_header")

        # The target is the output we would like
        targets = [
            f"{workflow_path}/tests/.test_output/rid_header_test/temp/vcf_no_header.vcf"
        ]

        # Remove the lock file if it exists
        os.system(
            f"snakemake -s {workflow_path}/workflow/Snakefile --unlock > /dev/null 2>&1"
        )

        # Change the config file parameters
        working_dir = f"{workflow_path}/tests/.test_output"
        vcf_file = f"{workflow_path}/tests/test_data/dummy_vcf/danio_rerio_100_test.vcf"
        name = "rid_header_test"
        out_name = "rid_header_test"

        # Run the Snakemake pipeline
        run_snakemake(
            snakefile=f"{workflow_path}/workflow/Snakefile",
            config_args=[
                f"working_directory={working_dir}",
                f"vcf_file={vcf_file}",
                f"name={name}",
                f"out_name={out_name}",
            ],
            extra_args=targets,
        )

        # Check to make sure that the output does not have the header
        with open(targets[0], "r") as f:
            lines = f.readlines()
            self.assertTrue(lines[0].startswith("#CHROM"))

        # Remove the output folder
        os.system(f"rm -r {workflow_path}/tests/.test_output/rid_header_test")

    def test_get_vcf_header(self):

        # Let the oberver know that we are testing the vcf_header rule
        prCyan("Currently testing: rule get_vcf_header")

        # The target is the output we would like
        targets = [
            f"{workflow_path}/tests/.test_output/rid_header_test/temp/vcf_header.txt"
        ]

        # Remove the lock file if it exists
        os.system(
            f"snakemake -s {workflow_path}/workflow/Snakefile --unlock > /dev/null 2>&1"
        )

        # Change the config file parameters
        working_dir = f"{workflow_path}/tests/.test_output"
        vcf_file = f"{workflow_path}/tests/test_data/dummy_vcf/danio_rerio_100_test.vcf"
        name = "rid_header_test"
        out_name = "rid_header_test"

        # Run the Snakemake pipeline
        run_snakemake(
            snakefile=f"{workflow_path}/workflow/Snakefile",
            config_args=[
                f"working_directory={working_dir}",
                f"vcf_file={vcf_file}",
                f"name={name}",
                f"out_name={out_name}",
            ],
            extra_args=targets,
        )

        # Check to make sure that the output is only the vcf header
        with open(targets[0], "r") as f:
            lines = f.readlines()
            self.assertTrue(lines[0].startswith("##fileformat"))
            for line in lines:
                self.assertTrue(line.startswith("##"))

        # Remove the output folder
        os.system(f"rm -r {workflow_path}/tests/.test_output/rid_header_test")


if __name__ == "__main__":
    unittest.main()
