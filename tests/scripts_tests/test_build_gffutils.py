##############################################################################
# Testing different functions of the build gffutils script
#
#
##############################################################################

import os
import sys
import gzip
import argparse
import gffutils
import pytest
import tempfile


# Add the path to the build_gffutils.py to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "sparcs", "sparcs_workflow", "scripts"))

# Import the functions from the build_gffutils.py script
from build_gffutils import is_gzipped, is_gff_gtf_file, print_red

def test_is_gzipped():
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

def test_is_gff_gtf_file():
    # Create temporary files for testing
    gff_file = tempfile.NamedTemporaryFile(suffix=".gff", delete=False)
    gtf_file = tempfile.NamedTemporaryFile(suffix=".gtf", delete=False)
    gzipped_gff_file = tempfile.NamedTemporaryFile(suffix=".gff", delete=False)
    gzipped_gtf_file = tempfile.NamedTemporaryFile(suffix=".gtf", delete=False)

    # Test with gff file
    with open(gff_file.name, "w") as f:
        f.write("##gff-version 3")

    assert is_gff_gtf_file(gff_file.name, gzip=is_gzipped(gff_file.name)) == True
    os.remove(gff_file.name)

    # Test with gtf file
    with open(gtf_file.name, "w") as f:
        f.write("#")

    assert is_gff_gtf_file(gtf_file.name, gzip=is_gzipped(gtf_file.name)) == True
    os.remove(gtf_file.name)

    # Test with gzipped gff file
    with open(gzipped_gff_file.name, "w") as f:
        f.write("##gff-version 3")
    os.system("gzip {}".format(gzipped_gff_file.name))

    assert is_gff_gtf_file(f"{gzipped_gff_file.name}.gz", gzip=True) == True

    os.remove(f"{gzipped_gff_file.name}.gz")

    # Test with gzipped gtf file
    with open(f"{gzipped_gtf_file.name}.gz", "w") as f:
        f.write("#")
    os.system("gzip {}".format(gzipped_gtf_file.name))

    assert is_gff_gtf_file(f"{gzipped_gtf_file.name}.gz", gzip=is_gzipped(f"{gzipped_gtf_file.name}.gz")) == True
    os.remove(f"{gzipped_gtf_file.name}.gz")
