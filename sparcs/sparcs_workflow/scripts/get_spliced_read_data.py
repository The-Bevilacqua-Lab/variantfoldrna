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
import pandas as pd
import json
import sys
from pyfaidx import Fasta
import subprocess
from mutalyzer_hgvs_parser import to_model
import os 

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
        length = len(genes[f"transcript:{transcript}"][0:].seq)
    except:
        try:
            length = len(genes[f"{transcript}"][0:].seq)
        
        except:
            return None

    # Check to make sure it is not too close to the 5' or 3' ends
    if five_prime_test(hgvs, 1, flank) and three_prime_test(hgvs, length, flank):
        return genes[f"transcript:{transcript}"][hgvs - flank - 2:hgvs + flank -1].seq
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
            if len(line) > 1:
                line[1] = line[1].strip("\n").split("=")[1]
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
    parser.add_argument("--ref-seqs", dest="ref", help="Reference Genome")
    parser.add_argument("--flank", dest="flank", help="SNP flanking length")
    parser.add_argument("--cds-pos", dest="cds_pos", help="CDS start")
    parser.add_argument("--gffread", dest="gffread", help="Gffread Table")
    parser.add_argument("--o", dest="output", help="Output File")
    args = parser.parse_args()

    # Get the CDS position dictionary 
    cds_dict = get_cdna_pos_dict(args.cds_pos)

    # Get the transcripts
    if os.path.isfile(args.ref + ".fai"):
        genes = Fasta(args.ref, build_index=False)
    else:
        genes = Fasta(args.ref)

    # Open the output files 
    fn = open(args.output, "w")
    no_match = open(args.output[:-4] + "_no_match.txt", "w")

    # Read in the file with the VEP predictions
    predictions = pd.read_csv(args.vcf, sep="\t", header=0)
    predictions = predictions.dropna()

    # Get the feature ID
    feature = "Feature"
  
    # Opening JSON file
    f = open(args.gffread)
    
    # returns JSON object as 
    # a dictionary
    transcript_data = json.load(f)
  
    # Iterate over the VEP predictions
    for i in range(len(predictions)):
        # Check to make sure it is not an INDEL
        if (
            len(predictions.iloc[i]["REF_ALLELE"]) > 1
            or len(predictions.iloc[i]["Allele"]) > 1
            or predictions.iloc[i]["Allele"] == "-" 
            or predictions.iloc[i]["REF_ALLELE"] == "-"
            or predictions.iloc[i]["Allele"] == 'N'
            or predictions.iloc[i]["REF_ALLELE"] == 'N'
            or 'intron_variant' in predictions.iloc[i]["Consequence"]
            or 'splice_acceptor_variant' in  predictions.iloc[i]["Consequence"]
        ):
            continue

        # Get the strand of the transcript
        strand = str(predictions.iloc[i]["STRAND"])

        # Get the hgvs of the SNP
        hgvs = f'{predictions.iloc[i]["HGVSc"]}'
        model = get_hgvs(hgvs)

        if model:

            # Parse the hgvs with mutalyzer_hgvs_parser
            parsed = model['variants'][0]['location']

            # Get the start and stop positions of where the CDS occurs in the cDNA
            if f"transcript:{predictions.iloc[i][feature]}" in cds_dict:
                if cds_dict[f"transcript:{predictions.iloc[i][feature]}"] != "None":
                    cds_start = cds_dict[f"transcript:{predictions.iloc[i][feature]}"][0]
                    cds_end = cds_dict[f"transcript:{predictions.iloc[i][feature]}"][1]
                else:
                    cds_start = 1

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

                        # Get the flanking sequence
                        flank_left = seq[:int(args.flank)]
                        flank_right = seq[int(args.flank) + 1:]

                        # Get the reference and alternative alleles
                        if strand == "-1":
                            reference =  compelement_dna(predictions.iloc[i]["REF_ALLELE"])
                            alternative =  compelement_dna(predictions.iloc[i]["Allele"])
                        else:
                            reference =  predictions.iloc[i]["REF_ALLELE"]
                            alternative =  predictions.iloc[i]["Allele"]

                        # Get the chromosome
                        chrom = predictions.iloc[i]["#Location"].split(":")[0]
                        chrom_position = int(predictions.iloc[i]["#Location"].split(":")[1])

                        # Get the chromosome coordinate
                        # Get the chromosome
                        chrom_pos = predictions.iloc[i]["#Location"].split(":")[1]

                        # Check to see if the SNP matches the alternative allele
                        if snp_seq == alternative:
                            ref = alternative
                            alt = reference
                            flank = flank_left + ref + flank_right
                            fn.write(
                                f'{chrom}\t{chrom_position}\t{position}\t{ref}\t{alt}\t{flank_left}\t{flank_right}\t{predictions.iloc[i][feature]}\tMATCHED_ALT\t{predictions.iloc[i]["Consequence"]}\t{predictions.iloc[i]["STRAND"]}\n'
                            )

                        # Check to see if the SNP matches the reference allele
                        elif snp_seq == reference:
                            ref = reference
                            alt = alternative
                            flank = flank_left + ref + flank_right
                            fn.write(
                                f'{chrom}\t{chrom_position}\t{position}\t{ref}\t{alt}\t{flank_left}\t{flank_right}\t{predictions.iloc[i][feature]}\tMATCHED_REF\t{predictions.iloc[i]["Consequence"]}\t{predictions.iloc[i]["STRAND"]}\n'
                            )

                        # If the SNP does not match the reference or alternative allele, then we skip it
                        else:
                            ref = alternative
                            alt = reference
                            no_match.write(
                                f'{chrom}\t{chrom_position}\t{position}\t{ref}\t{alt}\t{flank_left}\t{flank_right}\t{predictions.iloc[i][feature]}\n'
                            )
    no_match.close()
    fn.close()
