# -- Imports --#
import os
import sys
import gzip
import argparse
import pytest
import tempfile

# Add the path to the build_gffutils.py to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "sparcs", "sparcs_workflow", "scripts"))

from create_json_from_gffread_table import gffread_table_to_json

@pytest.fixture(scope="module")
def tmp_gffread_table(tmpdir_factory):
    # Create a temporary gffread table file
    tmp_file = tmpdir_factory.mktemp("data").join("tmp_gffread_table.txt")
    with open(tmp_file, "w") as f:
        f.write("gene1\tchr1\t100\t200\t+\n")
        f.write("prefix:gene2\tchr2\t300\t400\t-\n")
        f.write("gene3\tchr3\t500\t600\t+\n")
    yield tmp_file
    # Clean up the temporary file
    os.remove(tmp_file)

def test_multiple_entries_with_colon(tmp_gffread_table):
    # Call the function
    result = gffread_table_to_json(str(tmp_gffread_table))
    # Define the expected output
    expected = {
        "gene1": ["chr1", 100, 200],
        "gene2": ["chr2", 300, 400],
        "gene3": ["chr3", 500, 600]
    }
    # Check if the result matches the expected output
    assert result == expected