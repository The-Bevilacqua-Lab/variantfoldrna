##############################################################################
# Testing different functions of the chunk_vcf.py script
#
# Author: Kobie Kirven
##############################################################################

import os
import sys
import gzip
import argparse
import pytest
import tempfile


# Add the path to the build_gffutils.py to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "sparcs", "sparcs_workflow", "scripts"))

# Import the functions from the build_gffutils.py script
from chunk_vcf import split_file_by_line, get_vcf_len, is_gzipped, chunk_vcf
from utils import generate_dummy_vcf
import os

def test_get_vcf_len():
    """
    Test the get_vcf_len function
    """
    for i in range(1,100):
        vcf_file = tempfile.NamedTemporaryFile(suffix=".vcf", delete=False)
        vcf_file.close()
        os.system(f"cat {vcf_file.name}")

        # Create the dummy vcf file
        generate_dummy_vcf(i, vcf_file.name)
        assert get_vcf_len(vcf_file.name, gzip_file=is_gzipped(vcf_file.name)) == i

        # Gzip the dummy vcf file
        os.system(f"gzip {vcf_file.name}")
        assert get_vcf_len(f"{vcf_file.name}.gz", gzip_file=is_gzipped(f"{vcf_file.name}.gz")) == i
        os.remove(f"{vcf_file.name}.gz")


def test_is_gzipped():
    """
    Test the is_gzipped function
    """
    # Create temporary files for testing
    gzipped_file = tempfile.NamedTemporaryFile(suffix=".gz")
    ungziped_file = tempfile.NamedTemporaryFile()

    # Test with gzipped file
    with gzip.open(gzipped_file.name, "wb") as f:
        f.write(b"Test gzipped file")

    assert is_gzipped(gzipped_file.name) == True

    # Test with un-gzipped file
    with open(ungziped_file.name, "w") as f:
        f.write("Test un-gzipped file")

    assert is_gzipped(ungziped_file.name) == False

def test_split_file_by_line():
    """
    Test the split_file_by_line function
    """
    # Create temporary files for testing
    vcf_file = tempfile.NamedTemporaryFile(suffix=".vcf", delete=False)
    vcf_file.close()
    print(vcf_file.name)
    # Create the dummy vcf file
    generate_dummy_vcf(100, vcf_file.name)
    os.system(f"gzip {vcf_file.name}")


    for num_chunks in range(1,100):

        # Create a fake header file
        header_file = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
        header_file.close()
        header = open(header_file.name, "w")
        header.write("##fileformat=VCFv4.2\n")
        header.write("##fileDate=20190805\n")
        header.close()

        # Split the file into chunks
        chunk_vcf(f"{vcf_file.name}.gz", num_chunks, "test_chunkfile", header.name)
        
        # Check that the number of lines in each chunk is equal to the number of lines in the original file divided by the number of chunks
        # Get the files in the current directory
        files = os.listdir()

        # Get the files that start with "test_file_"
        test_files = [f for f in files if f.startswith("test_chunkfile")]

        # Check to make sure we have the correct number of chunks
        assert len(test_files) == num_chunks

        # Check to make sure the total number of lines in the chunks is equal to the number of lines in the original file
        total_lines = 0
        for f in test_files:
            os.system(f"gunzip {f}.gz")
            with open(f) as f:
                total_lines += sum(1 for line in f if line.startswith("#") == False)
        
        assert total_lines == 100

        # Remove the test files
        for f in test_files:
            os.remove(f)

    # Remove the original vcf file
    os.remove(f"{vcf_file.name}.gz")


