##############################################################################
# This script will test all of the rules in the snpeff.smk file
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

# Get the path to the workflow on the current computer
workflow_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
workflow_path = "/".join(workflow_path.split("/")[:-1])


def prCyan(skk):
    print("\033[96m {}\033[00m".format(skk))


# Remove the output directory if it already exists
if os.path.exists(f"{workflow_path}/tests/.test_output/snpeff_test"):
    os.system(f"rm -rf {workflow_path}/tests/.test_output/snpeff_test")


class TestPipeline(unittest.TestCase):
    # def test_add_gtf(self):
    #     """ "
    #     Test the add_gtf rule. Should copy the gtf file to the output directory for future
    #     creation of the SnpEff database.
    #     """
    #     # Let the oberver know that we are testing the add_gtf rule
    #     prCyan("Currently testing: rule add_gtf")

    #     # Targets
    #     targets = ["add_gtf"]

    #     gtf_file = f"{workflow_path}/tests/test_data/snpeff/test_gtf.gtf"
    #     working_dir = f"{workflow_path}/tests/.test_output"

    #     # Run the snakemake pipeline
    #     run_snakemake(
    #         snakefile=f"{workflow_path}/workflow/Snakefile",
    #         config_args=[
    #             f"gtf_file={gtf_file}",
    #             f"working_directory={working_dir}",
    #             "name=snpeff_test",
    #             "out_name=snpeff_test",
    #         ],
    #         extra_args=targets,
    #     )
    #     os.system(
    #         f"gunzip {workflow_path}/tests/.test_output/snpeff_test/temp/data/snpeff_test/genes.gtf.gz"
    #     )

    #     # Check to make sure the new gtf file is the same as the original
    #     first = f"{workflow_path}/tests/.test_output/snpeff_test/temp/data/snpeff_test/genes.gtf"
    #     second = f"{workflow_path}/tests/test_data/snpeff/test_gtf.gtf"

    #     # Check equal
    #     diff = subprocess.run(["diff", first, second], stdout=subprocess.PIPE)
    #     self.assertEqual(diff.stdout, b"")

    #     # Remove the output directory
    #     os.system(f"rm -r {workflow_path}/tests/.test_output/snpeff_test")

    def test_add_ref(self):
        """
        Test the add_ref rule. Should copy the reference file to the output directory for future
        creation of the SnpEff database.
        """
        # Let the oberver know that we are testing the add_ref rule
        prCyan("Currently testing: rule add_ref")

        # Targets
        targets = ["add_ref"]

        # Get the reference genome and working directory
        ref_file = f"{workflow_path}/tests/test_data/snpeff/test_ref.fasta"
        working_dir = f"{workflow_path}/tests/.test_output"

        # Run the snakemake pipeline
        run_snakemake(
            snakefile=f"{workflow_path}/workflow/Snakefile",
            config_args=[
                f"ref_genome={ref_file}",
                f"working_directory={working_dir}",
                "name=snpeff_test",
                "out_name=snpeff_test",
            ],
            extra_args=targets,
        )

        # Check to make sure the new gtf file is the same as the original
        with open(
            f"{workflow_path}/tests/.test_output/snpeff_test/temp/data/genomes/snpeff_test.fa"
        ) as fn:
            with open(f"{workflow_path}/tests/test_data/snpeff/test_ref.fasta") as fn2:
                self.assertEqual(fn.read(), fn2.read())

        # Remove the output directory
        os.system(f"rm -r {workflow_path}/tests/.test_output/snpeff_test")

    # def test_create_config(self):
    #     """
    #     Test that the create_config rule creates the correct config file for SnpEff.
    #     """
    #     # Targets
    #     targets = ["create_config"]

    #     name, out_name = "snpeff_test", "snpeff_test"
    #     working_dir = f"{workflow_path}/tests/.test_output"

    #     # Run the snakemake pipeline
    #     run_snakemake(snakefile=f"{workflow_path}/workflow/Snakefile", config_args=[f"working_directory={working_dir}", f"name={name}", f"out_name={out_name}"], extra_args=targets)

    #     # Check to make sure the config file is correct
    #     with open(f"{workflow_path}/tests/.test_output/snpeff_test/temp/snpeff.config") as fn:
    #         lines = fn.readlines()
    #         self.assertEqual(lines[0], f"snpeff_test.genome: snpeff_test\n")

    # def test_create_snpeff_db(self):
    #     """
    #     Test to make sure that the SnpEff database is created correctly.
    #     """
    #     pass

    # def test_seperate_multi_vars(self):
    #     """
    #     Test to make sure that the multi-allelic variants are separated correctly.
    #     """
    #     # Create the output directory
    #     try:
    #         os.system(f"mkdir -p {workflow_path}/tests/.test_output/snpeff_test/temp/vcf_chunks/")
    #     except:
    #         pass

    #     # Copy the multi-allelic vcf file to the output directory
    #     os.system(f"cp {workflow_path}/tests/test_data/snpeff/test_multi.vcf {workflow_path}/tests/.test_output/snpeff_test/temp/vcf_chunks/vcf_no_header_1.vcf")

    #     # Get the new arguments for the config
    #     targets = [f"{workflow_path}/tests/.test_output/snpeff_test/temp/vcf_chunks/vcf_no_header_1_seperated.vcf.gz"]
    #     name, out_name = "snpeff_test", "snpeff_test"
    #     chunks = 1
    #     working_dir = f"{workflow_path}/tests/.test_output"

    #     # Run the snpEff pipeline
    #     run_snakemake(snakefile=f"{workflow_path}/workflow/Snakefile", config_args=[f"working_directory={working_dir}", f"name={name}", f"out_name={out_name}", f"chunks={chunks}"], extra_args=targets)

    #     # Unzip the bgzipped output file
    #     os.system(f"bgzip -d {workflow_path}/tests/.test_output/snpeff_test/temp/vcf_chunks/vcf_no_header_1_seperated.vcf.gz")

    #     # Check to make sure that the output file now has 30 lines that do
    #     # not start with '#' and the number of alternative alleles is 1
    #     with open(f"{workflow_path}/tests/.test_output/snpeff_test/temp/vcf_chunks/vcf_no_header_1_seperated.vcf") as fn:
    #         lines = fn.readlines()
    #         count = 0
    #         for line in lines:
    #             if line[0] != "#":
    #                 count += 1
    #                 self.assertEqual(len(line.split("\t")[4].split(",")), 1)

    #         self.assertEqual(count, 30)

    # def test_normalize(self):
    #     """
    #     Test to make sure that the variants are normalized correctly.
    #     """
    #     pass

    # def test_run_snpeff(self):
    #     """
    #     Test to make sure that the SnpEff annotation is run correctly.
    #     """
    #     pass

    # def test_get_annotations_one_per_line(self):
    #     """
    #     Test to make sure that the snpeff annotations are correctly
    #     seperated into one per-line
    #     """
    #     # Create the output directory
    #     try:
    #         os.system(f"mkdir -p {workflow_path}/tests/.test_output/snpeff_test/temp/annotated_vcf_chunks/")
    #     except:
    #         pass

    # Copy the multi-annotated vcf file to the output directory
    # os.system(f"cp {workflow_path}/tests/test_data/snpeff/test_annotated_vcf.vcf {workflow_path}/tests/.test_output/snpeff_test/temp/annotated_vcf_chunks/vcf_no_header_1_annotated.vcf")

    # # Get the new arguments for the config
    # targets = [f"{workflow_path}/tests/.test_output/snpeff_test/temp/annotated_vcf_chunks_effects/vcf_no_header_1_annotated_one_per_line.txt"]

    # name, out_name = "snpeff_test", "snpeff_test"
    # chunks = 1
    # working_dir = f"{workflow_path}/tests/.test_output"

    # # Run the snpEff pipeline
    # run_snakemake(snakefile=f"{workflow_path}/workflow/Snakefile", config_args=[f"working_directory={working_dir}", f"name={name}", f"out_name={out_name}", f"chunks={chunks}"], extra_args=targets)

    # # Check to make sure that the output file now has 11 lines that do not start with '#'
    # with open(f"{workflow_path}/tests/.test_output/snpeff_test/temp/annotated_vcf_chunks_effects/vcf_no_header_1_annotated_one_per_line.txt") as fn:
    #     lines = fn.readlines()
    #     self.assertEqual(len(lines), 12)


if __name__ == "__main__":
    unittest.main()
