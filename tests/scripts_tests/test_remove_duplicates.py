##############################################################################
# Testing different functions of the drop_duplicates.py script
#
# Author: Kobie Kirven
##############################################################################

# -- Imports --#
import os
import sys
import tempfile
import subprocess
import random 


# Add the path to the build_gffutils.py to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "sparcs", "sparcs_workflow", "scripts"))
path = os.path.join(os.path.dirname(__file__), "..", "..", "sparcs", "sparcs_workflow", "scripts", "remove_duplicates.py")


def generate_tab_file(n, t):
    """
    Generates a .tab file with n lines and t duplicated lines.
    """
    # Create a temporary file for testing
    temporary_file = tempfile.NamedTemporaryFile(suffix=".tab", delete=False)
    temporary_file.close()

    # Generate random number 
    random.seed(0)

    with open(temporary_file.name, "w") as f:
        for i in range(n):
            random_number = random.randint(0, 1000000)
            for j in range(t):
                f.write("chr1\t1\t2\tgene\t\t" + str(random_number) +  "\t1\t2\t0\t1\t1\t0\n")

    return temporary_file.name

def test_drop_duplicates():
    for i in range(1, 10):
        for j in range(1, 10):
            # Generate a tab file with i lines and j duplicated lines
            tab_file = generate_tab_file(i, j)
            print(tab_file)

            # Run the drop_duplicates.py script
            subprocess.run(["python3", path, "-i", tab_file, "-o", tab_file + ".out"])

            # Check that the output file has the correct number of lines
            with open(tab_file + ".out") as f:
                assert len([x for x in f.readlines()]) == i

            # Remove the temporary files
            os.remove(tab_file)
            os.remove(tab_file + ".out")


