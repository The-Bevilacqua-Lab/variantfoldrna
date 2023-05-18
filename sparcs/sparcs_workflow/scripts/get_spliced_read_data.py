#!/usr/bin/env python3
################################################################################
# Rice riboSNitch analysis: Collect the sequence data to be run for the
# different riboSNitch prediction tools
#
# Author: Kobie Kirven
################################################################################

# Goal: Get a file with the reference sequence and the sequence with the
# alternative allele.


# ----- Import modules ----#
import argparse
import gffutils
import pandas as pd
import json
import sys
from pyfaidx import Fasta
import subprocess
from mutalyzer_hgvs_parser import to_model

# ----- Functions ------#

# ----- Functions ------#
def compelement_dna(dna):
    """
    Get the complement of a DNA sequence
    Parameters:
    - dna (str): DNA sequence
    Returns:
    - (str): Complement of the DNA sequence
    """
    complement = {"A": "T", "C": "G", "G": "C", "T": "A", "N": "N"}
    return "".join([complement[base.upper()] for base in dna])


def five_prime_test(position, start, flank):
    """
    Test to make sure the SNP is far enough away from the
    5' end of the transcript
    """
    if int(position) > (int(start) + (int(flank) - 1)):
        return True
    else:
        return False


def three_prime_test(position, end, flank):
    """
    Test to make sure the SNP is far enough away from the
    3' end of the transcript
    """
    if int(position) < (int(end) - (int(flank) - 1)):
        return True
    else:
        return False


def get_cdna(hgvs, flank, genes, transcript):
    """
    Get the location of the SNP in the cDNA
    """
    # hgvs = hgvs -1 
    try:
        length = len(genes[transcript][0:].seq)
    except:
        try:
            length = len(genes[f"{transcript}.1"][0:].seq)
            # Check to make sure it is not too close to the 5' or 3' ends
            if five_prime_test(hgvs, 1, flank) and three_prime_test(hgvs, length, flank):
                return genes[f"{transcript}.1"][hgvs - flank+1:hgvs + flank+1].seq
        except:
            return None

    # Check to make sure it is not too close to the 5' or 3' ends
    if five_prime_test(hgvs, 1, flank) and three_prime_test(hgvs, length, flank):
        return genes[transcript][hgvs - flank - 2:hgvs + flank -1].seq
    else:
        return None

def get_cdna_pos_dict(cdna_pos_file):
    """
    Create a dictionary with the start and stop positions for the CDS for each transcript. 
    """
    cds_dict = {}
    with open(cdna_pos_file) as fn:
        for line in fn:
            line = line.split(" ")
            # print(line)
            if len(line) > 1:
                line[1] = line[1].strip("\n").split("=")[1]
                # print(line)
                cds_dict[line[0][1:].strip("\n")] = [line[1].split("-")[0], line[1].split("-")[1]]
            else:
                cds_dict[line[0][1:].strip("\n")] = "None"
    return cds_dict

def get_hgvs(hgvs):
    return to_model(hgvs)
# -- main --#

if __name__ == "__main__":

    # ----- Parse arguments ----#
    parser = argparse.ArgumentParser(
        description="Extract sequences surrounding variants"
    )
    parser.add_argument("--vcf", dest="vcf", help="VCF File")
    parser.add_argument("--database", dest="database", help="gffutils database")
    parser.add_argument("--ref-seqs", dest="ref", help="Reference Genome")
    parser.add_argument("--flank", dest="flank", help="SNP flanking length")
    parser.add_argument("--cds-pos", dest="cds_pos", help="CDS start")
    parser.add_argument("--o", dest="output", help="Output File")
    args = parser.parse_args()

    # Get the CDS position dictionary 
    cds_dict = get_cdna_pos_dict(args.cds_pos)

    # load the GFFUtils database
    db = gffutils.FeatureDB(args.database, keep_order=True)

    # Get the genes
    genes = Fasta(args.ref)

    # Open the output files 
    fn = open(args.output, "w")
    no_match = open(args.output[:-4] + "_no_match.txt", "w")

    # Read in the file with the SNPEff predictions
    predictions = pd.read_csv(args.vcf, sep="\t", header=0)
    predictions = predictions.dropna()

    # Get the feature ID
    feature = "ANN[*].FEATUREID"
    for i in range(len(predictions)):
        # Check to make sure it is not an INDEL
        if len(predictions.iloc[i]["REF"]) == 1 and len(predictions.iloc[i]["ALT"]) == 1:

            # Get the strand of the transcript
            strand = db[predictions.iloc[i][feature]].strand

            # Complement the reference and alternative alleles if the transcript is on the negative strand
            if db[predictions.iloc[i][feature]].strand == "-":
                reference = compelement_dna(predictions.iloc[i]["REF"])
                alternative = compelement_dna(predictions.iloc[i]["ALT"])

            elif db[predictions.iloc[i][feature]].strand == "+":
                reference = predictions.iloc[i]["REF"]
                alternative = predictions.iloc[i]["ALT"]

            # Get the hgvs of the SNP
            hgvs = f'{predictions.iloc[i][feature]}:{predictions.iloc[i]["ANN[*].HGVS_C"]}'

            model = get_hgvs(hgvs)

            if model:
                # Parse the hgvs with mutalyzer_hgvs_parser
                parsed = model['variants'][0]['location']

                # Get the start and stop positions of where the CDS occurs in the cDNA
                if predictions.iloc[i][feature] in cds_dict:
                    if cds_dict[predictions.iloc[i][feature]] != "None":
                        cds_start = cds_dict[predictions.iloc[i][feature]][0]
                        cds_end = cds_dict[predictions.iloc[i][feature]][1]
                    else:
                        cds_start = 0

                    if 'offset' not in parsed:
                        if 'outside_cds' in parsed:
                            if parsed['outside_cds'] == 'downstream':
                                position = int(cds_end) + int(parsed['position']) + 1
                            elif parsed['outside_cds'] == 'upstream':
                                position = int(cds_start) - int(parsed['position']) + 1
                            else:
                                continue 
                        else:
                            position = int(cds_start) + int(parsed['position']) 

                        seq = get_cdna(position, int(args.flank), genes, predictions.iloc[i][feature])

                        if seq:
                            snp_seq = seq[int(args.flank)]
                            if snp_seq == alternative:
                                ref = alternative
                                alt = reference
                                flank = seq
                                flank_left = seq[0:int(args.flank)]
                                flank_right = seq[int(args.flank) + 1:]
                                fn.write(
                                    f'{predictions.iloc[i]["CHROM"]}\t{predictions.iloc[i]["POS"]}\t{ref}\t{alt}\t{flank_left}\t{flank_right}\t{predictions.iloc[i][feature]}\tMATCHED_ALT\t{db[predictions.iloc[i][feature]].featuretype}\t{db[predictions.iloc[i][feature]].strand}\t{predictions.iloc[i]["ANN[*].EFFECT"]}\n'
                                )
                            elif snp_seq == reference:
                                ref = reference
                                alt = alternative
                                flank = seq
                                flank_left = seq[0:int(args.flank)]
                                flank_right = seq[int(args.flank) + 1:]
                                fn.write(
                                    f'{predictions.iloc[i]["CHROM"]}\t{predictions.iloc[i]["POS"]}\t{ref}\t{alt}\t{flank_left}\t{flank_right}\t{predictions.iloc[i][feature]}\tMATCHED_REF\t{db[predictions.iloc[i][feature]].featuretype}\t{db[predictions.iloc[i][feature]].strand}\t{predictions.iloc[i]["ANN[*].EFFECT"]}\n'
                                )

                            # If the SNP does not match the reference or alternative allele, then we skip it
                            else:
                                flank = seq
                                no_match.write(
                                    f'{predictions.iloc[i][feature]}\t{predictions.iloc[i]["POS"]}\t{flank}\t{predictions.iloc[i]["REF"]}\t{predictions.iloc[i]["ALT"]}\t{db[predictions.iloc[i][feature]].strand}\t{predictions.iloc[i]["ANN[*].EFFECT"]}\n'
                            )
                else:
                    print(f"NOT HERE:{predictions.iloc[i][feature]}")
    no_match.close()
    fn.close()
