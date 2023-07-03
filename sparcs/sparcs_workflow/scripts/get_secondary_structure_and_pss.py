###########################################################
# Get the secondary structure and the probability of pairin
# from the output of RNAfold
###########################################################

import tempfile
import random
import subprocess
import string
import os
import numpy as np
import argparse
import pandas as pd

def get_temp_fasta(sequence):
    """
    Writes a temporary fasta file with the given sequence
    """
    fn = tempfile.NamedTemporaryFile(delete=False)
    name = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(6)
    )
    fn.write(b">.sq" + name.encode("utf-8") + b"\n")
    fn.write(sequence.encode("utf-8"))
    return fn.name, name


def get_bppm(sequence):
    """
    Runs RNAfold on the given sequence and returns the base pair probibility matrix
    """
    temp_fasta, name = get_temp_fasta(sequence)
    bpp = subprocess.check_output(
        ["RNAfold", "-p", "-i", temp_fasta]
    ).decode("utf-8")

    secondary = bpp.split("\n")[2].split(" ")[0]
    bpp_matrix = np.zeros((len(sequence), len(sequence)), dtype=float)


    with open(".sq" + name + "_dp.ps") as fn:
        lines = fn.readlines()
        for line in lines:
            if "ubox\n" in line:
                line = line.split(" ")
                if len(line) == 4:
                    if line[3] == "ubox\n":
                        bpp_matrix[int(line[0]) - 1, int(line[1]) - 1] = float(
                            line[2]
                        ) * float(line[2])
                        bpp_matrix[int(line[1]) - 1, int(line[0]) - 1] = float(
                            line[2]
                        ) * float(line[2])
    os.remove(temp_fasta)
    try:
        os.remove(".sq" + name + "_ss.ps")
        os.remove(".sq" + name + "_dp.ps")
    except:
        pass
    return bpp_matrix, secondary

def get_column_sums(bpp_matrix):
    """
    Returns the sum of each column of the base pair probability matrix
    """
    return np.sum(bpp_matrix, axis=0)


if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Get secondary structure")
    parser.add_argument("--i", dest="in_file", help="Input File")
    parser.add_argument("--o", dest="output", help="Output")
    args = parser.parse_args()
    
    # Read in the input file as a pandas dataframe
    df = pd.read_csv(args.in_file, sep="\t", header=0)

    # Get the secondary structure and the probability of pairing
    ref_seqs = []
    alt_seqs = []
    ref_bppms = []
    alt_bppms = []
    ref_secondarys = []
    alt_secondarys = []

    for i in range(len(df)):
        seq = df.iloc[i]["Flank_left"].replace("T", "U") + df.iloc[i]["Ref"] + df.iloc[i]["Flank_right"].replace("T", "U")
        bppm, secondary = get_bppm(seq)
        ref_seqs.append(seq)
        ref_bppms.append(",".join(list(get_column_sums(bppm).astype(str))))
        ref_secondarys.append(secondary)

        seq = df.iloc[i]["Flank_left"].replace("T", "U") + df.iloc[i]["Alt"] + df.iloc[i]["Flank_right"].replace("T", "U")
        bppm, secondary = get_bppm(seq)
        alt_seqs.append(seq)
        alt_bppms.append(",".join(list(get_column_sums(bppm).astype(str))))
        alt_secondarys.append(secondary)

    # Create a new dataframe with the secondary structure and the probability of pairing
    df = pd.DataFrame()
    df["Ref_Sequence"] = ref_seqs
    df["Ref_BPPM"] = ref_bppms
    df["Ref_Secondary"] = ref_secondarys
    df["Alt_Sequence"] = alt_seqs
    df["Alt_BPPM"] = alt_bppms
    df["Alt_Secondary"] = alt_secondarys
    
    # Write the dataframe to a file
    df.to_csv(args.output, sep="\t", index=False)
