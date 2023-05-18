################################################################################
# Wrapper for get_ensemble_diversity.py
#
# Author: Kobie Kirven
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
    Create a temporary fasta file
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
            ["RNAfold", "-p", ref_fn, "-T", temp, "--noPS", "--noDP"], stdout=subprocess.PIPE
        )
        alt = subprocess.run(
            ["RNAfold", "-p", alt_fn, "-T", temp,"--noPS", "--noDP"], stdout=subprocess.PIPE
        )
    except:
        return "Error"

    # Get the delta ensemble diversity
    ref = [x for x in ref.stdout.decode('utf-8').split('\n')[-2].split(" ") if x != ""][-1]
    alt = [x for x in alt.stdout.decode('utf-8').split('\n')[-2].split(" ") if x != ""][-1]
    delta = float(ref) - float(alt)

    # Clean up
    os.remove(ref_fn)
    os.remove(alt_fn)

    return delta


def get_delta_ensemble_free_energy(ref_seq, alt_seq, temp):
    """
    Get the delta ensemble diversity for a variant
    """
    # Create temporary fasta files
    ref_fn, ref_name = create_temporary_fasta(ref_seq)
    alt_fn, alt_name = create_temporary_fasta(alt_seq)

    # Run RNAfold
    try:
        ref = subprocess.run(
            ["RNAfold", "-p", ref_fn, "-T", temp, "--noPS", "--noDP"], stdout=subprocess.PIPE
        )
        alt = subprocess.run(
            ["RNAfold", "-p", alt_fn, "-T", temp,"--noPS", "--noDP"], stdout=subprocess.PIPE
        )
    except:
        return "Error"

    # Get the delta ensemble diversity
    ref = ref.stdout.decode("utf-8").split("\n")[3].split(" ")[-1][1:-1]
    alt = alt.stdout.decode("utf-8").split("\n")[3].split(" ")[-1][1:-1]
    delta = float(ref) - float(alt)

    # Clean up
    os.remove(ref_fn)
    os.remove(alt_fn)

    return delta


if __name__ == "__main__":
    # Parse the arguments
    parser = argparse.ArgumentParser(description="Determine delta ensemble diversity or free energy")
    parser.add_argument("--i", dest="in_file", help="Input File")
    parser.add_argument("--o", dest="output", help="Output")
    parser.add_argument("--temp", dest="temp", help="Temp")
    parser.add_argument("--tool-type", dest="type_tool", help="Type")
    args = parser.parse_args()

    # Open the output files
    outfile = open(args.output, "w")
    error = open(args.output.strip(".txt") + "_error.txt", "w")

    ids, seqs = [], []
    with open(args.in_file) as fn:
        for line in fn:

            # Skip the header
            if not line.startswith("#"):
                line = line.split("\t")

                # Check to make sure we don't have any indels
                if not len(line[2]) == 1 or not len(line[3]) == 1:
                    continue

                # Change the reference and alternative alleles
                if line[2] == "T":
                    line[2] = "U"
                if line[3] == "T":
                    line[3] = "U"

                # Get the sequence and the mutation
                ref = str(line[4]) + str(line[2]) + str(line[5])
                alt = str(line[4]) + str(line[3]) + str(line[5])

                if args.type_tool.lower() == "delta_ensemble_diversity":
                    # Get the delta ensemble diversity
                    results = get_delta_ensemble_diversity(ref, alt, args.temp)

                elif args.type_tool.lower() == "delta_ensemble_free_energy":
                    # Get the delta ensemble free energy
                    results = get_delta_ensemble_free_energy(ref, alt, args.temp)
                
                else:
                    print("Error: Invalid type")
                    exit()

                # Write the results to the output file
                try:
                    previous = "\t".join(line).strip("\n")
                    outfile.write(f"{previous}\t{results}\n")
                except:
                    error.write("\t".join(line) + "\n")

    # Close the output and error files
    fn.close()
    error.close()
