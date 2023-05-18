################################################################################
# Get the delta-ensemble diversity for each variant
#
# Author: Kobie Kirven
# Assmann and Bevilacqua Labs -- The Pennsylvania State University
################################################################################

# ----- Import modules ----#
import argparse
import subprocess
import tempfile
import os
import string
import random


# ----- Functions ------#
def create_temporary_fasta(seq):
    """
    Create a temporary fasta fil
    """
    fn = tempfile.NamedTemporaryFile(delete=False)
    name = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(6)
    )
    fn.close()
    with open(fn.name, "w") as f:
        f.write(">{0}\n".format(name))
        f.write("{0}\n".format(seq))
    return fn.name, name
    

def get_delta_ensemble_diversity(ref_seq, alt_seq, temp):
    """
    Get the delta ensemble diversity for a variant
    """
    # Create temporary fasta files
    ref_fn, ref_name = create_temporary_fasta(ref_seq)
    alt_fn, alt_name = create_temporary_fasta(alt_seq)

    # Run RNAfold
    try:
        ref = subprocess.run(
            ["RNAfold", "-p", ref_fn, "-T", temp], stdout=subprocess.PIPE
        )
        alt = subprocess.run(
            ["RNAfold", "-p", alt_fn, "-T", temp], stdout=subprocess.PIPE
        )
    except:
        return "Error"

    # Get the delta ensemble diversity
    ref = ref.stdout.decode("utf-8").split("\n")[2].split(" ")[-1]
    alt = alt.stdout.decode("utf-8").split("\n")[2].split(" ")[-1]
    delta = float(ref) - float(alt)

    # Clean up
    os.remove(ref_fn)
    os.remove(alt_fn)

    return delta

# ----- Main ------#
if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref", help="Reference sequence")
    parser.add_argument("--alt", help="Alternate sequence")
    parser.add_argument("--temp", help="Temperature")
    args = parser.parse_args()

    # Get the delta ensemble diversity
    delta = get_delta_ensemble_diversity(args.ref, args.alt)

    # Print the delta ensemble diversity
    print(delta)