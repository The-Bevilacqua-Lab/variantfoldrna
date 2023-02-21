##############################################################################
# This script will test all of the rules in the chunk.smk file
#
# Author: Kobie Kirven
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
##############################################################################

# Imports
import os
import unittest
from utils import *
import gzip 

#######################################
# Prepare the config file for testing #
#######################################
workflow_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
workflow_path = "/".join(workflow_path.split("/")) + "/tests"

class TestPipeline(unittest.TestCase):
    def test_chunk_vcf_gzip(self):
        """
        Test that the chunk_vcf rule works as expected

        This test will run the chunk_vcf rule with a range of chunk sizes
        and check to make sure that the correct number of files are outputted. 
        """
        add_workflow()

        chunks = range(1, 11)

        prCyan("Currently Testing: rule chunk_vcf")
        for chunk in chunks:
            # Targets
            targets = ["chunk_vcf"]

            # Make sure that no locks exist on the pipeline
            os.system(
                f"snakemake -s --unlock > /dev/null 2>&1"
            )

            # Change the config file paramaters
            working_dir = f"{workflow_path}/.test_output"
            vcf_file = (
                f"{workflow_path}/test_data/dummy_vcf/danio_rerio_100_test_1.vcf.gz"
            )
            name = "chunk_test"
            out_name = "chunk_test"
            chunk_size = chunk

            # Create the config file to be used for the test
            config_builder(
                f"{workflow_path}/workflow/config.yaml",
                working_dir,
                vcf_file,
                "NA",
                "NA",
                out_name,
                10,
                chunk_size,
                10,
                "NA",
                "NA",
                "NA"
            )

            # Run the snakemake pipeline
            run_snakemake(
                snakefile=f"{workflow_path}/workflow/sparcs.rules",
                extra_args=targets,
            )

            # Check to make sure we have the correct number of output files
            files = os.listdir(
                f"{workflow_path}/.test_output/chunk_test/temp/vcf_chunks"
            )
            self.assertEqual(len(files), chunk)

            # Check to make sure we have 82 lines in total that do not have a "#"
            total_lines = 0
            for file in files:
                with gzip.open(
                    f"{workflow_path}/.test_output/chunk_test/temp/vcf_chunks/{file}"
                , "rb") as fn:
                    for line in fn:
                        line = line.decode("utf-8")
                        if not line.startswith("#"):
                            total_lines += 1
            self.assertEqual(total_lines, 82)

            # Remove the output directory
            os.system(f"rm -rf {workflow_path}/.test_output/chunk_test")
        remove_workflow()
            
    def test_chunk_vcf(self):
        """
        Test that the chunk_vcf rule works as expected

        This test will run the chunk_vcf rule with a range of chunk sizes
        and check to make sure that the correct number of files are outputted. 
        """
        add_workflow()

        chunks = range(1, 11)

        prCyan("Currently Testing: rule chunk_vcf")
        for chunk in chunks:
            # Targets
            targets = ["chunk_vcf"]

            # Make sure that no locks exist on the pipeline
            os.system(
                f"snakemake -s --unlock > /dev/null 2>&1"
            )

            # Change the config file paramaters
            working_dir = f"{workflow_path}/.test_output"
            vcf_file = (
                f"{workflow_path}/test_data/dummy_vcf/danio_rerio_100_test.vcf"
            )
            name = "chunk_test"
            out_name = "chunk_test"
            chunk_size = chunk

            # Create the config file to be used for the test
            config_builder(
                f"{workflow_path}/workflow/config.yaml",
                working_dir,
                vcf_file,
                "NA",
                "NA",
                out_name,
                10,
                chunk_size,
                10,
                "NA",
                "NA",
                "NA"
            )

            # Run the snakemake pipeline
            run_snakemake(
                snakefile=f"{workflow_path}/workflow/sparcs.rules",
                extra_args=targets,
            )

            # Check to make sure we have the correct number of output files
            files = os.listdir(
                f"{workflow_path}/.test_output/chunk_test/temp/vcf_chunks"
            )
            self.assertEqual(len(files), chunk)

            # Check to make sure we have 82 lines in total that do not have a "#"
            total_lines = 0
            for file in files:
                with gzip.open(
                    f"{workflow_path}/.test_output/chunk_test/temp/vcf_chunks/{file}"
                , "rb") as fn:
                    for line in fn:
                        line = line.decode("utf-8")
                        if not line.startswith("#"):
                            total_lines += 1
            self.assertEqual(total_lines, 82)

            # Remove the output directory
            os.system(f"rm -rf {workflow_path}/.test_output/chunk_test")
        remove_workflow()

    def test_chunk_extracted_sequences(self):
        """
        Test that the chunk_extracted_sequences rule works as expected
        """
        # Copy the workflow to the test directory
        add_workflow()

        # Copy the test data to the output directory
        if not os.path.exists(f"{workflow_path}/.test_output/chunk_test/temp"):
            os.system(f"mkdir -p {workflow_path}/.test_output/chunk_test/temp")

        # Copy the test data to the appropriate directory
        if not os.path.exists(
            f"{workflow_path}/.test_output/chunk_test/temp/extracted_flank_snp_no_duplicates.txt"
        ):
            os.system(
                f"cp -r {workflow_path}/test_data/chunk_extracted_sequences/extracted_sequences_test.txt {workflow_path}/.test_output/chunk_test/temp/extracted_flank_snp_no_duplicates.txt"
            )

        # Targets
        targets = ["chunk_extracted_sequences"]

        # Let the audience know what we are testing 
        prCyan("Currently Testing: rule chunk_extracted_sequences")

        # Chunk range to test
        chunks = range(1, 12)

        # Loop through the chunks
        for chunk in chunks:
            
            # Make sure that no locks exist on the pipeline
            os.system(
                f"snakemake --unlock > /dev/null 2>&1"
            )

            # Change the config file paramaters
            working_dir = f"{workflow_path}/.test_output"
            vcf_file = (
                f"{workflow_path}/test_data/dummy_vcf/danio_rerio_100_test.vcf"
            )
            name = "chunk_test"
            out_name = "chunk_test"
            chunk_size = chunk

            config_builder(
                f"{workflow_path}/workflow/config.yaml",
                working_dir,
                vcf_file,
                "NA",
                "NA",
                out_name,
                10,
                chunk_size,
                10,
                "NA",
                "NA",
                "NA"
            )

            # Run the snakemake pipeline
            run_snakemake(
                snakefile=f"{workflow_path}/workflow/sparcs.rules",
                extra_args=targets,
            )

            # Check to make sure we have the correct number of output files
            files = os.listdir(
                f"{workflow_path}/.test_output/chunk_test/temp/extracted_seqs_chunks"
            )

            self.assertEqual(len(files), chunk)

            # Check to make sure we have 82 lines in total that do not have a "#"
            total_lines = 0
            for file in files:
                with open(
                    f"{workflow_path}/.test_output/chunk_test/temp/extracted_seqs_chunks/{file}"
                ) as fn:
                    for line in fn:
                        if not line.startswith("#"):
                            total_lines += 1
            self.assertEqual(total_lines, 11)

            # Remove the output directory
            os.system(
                f"rm -rf {workflow_path}/.test_output/chunk_test/temp/extracted_seqs_chunks"
            )

        # Remove the output directory
        os.system("rm -rf {workflow_path}/.test_output/chunk_test/")
        remove_workflow()


if __name__ == "__main__":
    unittest.main()
