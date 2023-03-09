##############################################################################
# Testing different functions of the chunk_extracted_seqs.py script
#
# Author: Kobie Kirven
##############################################################################

import os
import sys
import gzip
import argparse
import pytest
import tempfile
import tempfile

# Add the path to the build_gffutils.py to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "sparcs", "sparcs_workflow", "scripts"))

# Import the functions from the build_gffutils.py script
from chunk_extracted_seqs import split_file_by_line

def test_split_file_by_line():
    # Generate a random number of lines between 1 and 99
    num_lines = 100

    # Create a list of lines for the test file
    lines = [f"This is line {i+1}\n" for i in range(num_lines)]

    # Write the lines to a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.writelines(lines)
        filename = f.name

    for num_chunks in range(1,100):
        for i, chunk in enumerate(split_file_by_line(filename, num_chunks)):
            with open(f"test_file_{i}.txt", "w") as f:
                f.writelines(chunk)
        
        # Check to make sure we have the correct number of chunks
        # Get the files in the current directory
        files = os.listdir()
        # Get the files that start with "test_file_"
        test_files = [f for f in files if f.startswith("test_file_")]
        # Check to make sure we have the correct number of chunks
        assert len(test_files) == num_chunks

        # Check to make sure the total number of lines in the chunks is equal to the number of lines in the original file
        total_lines = 0
        for test_file in test_files:
            with open(test_file) as f:
                total_lines += len(f.readlines())
        assert total_lines == num_lines

        # Remove the test files
        for test_file in test_files:
            os.remove(test_file)


    # Clean up the temporary test file
    os.remove(filename)
