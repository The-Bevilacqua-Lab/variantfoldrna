#!/usr/bin/env python3
################################################################################
# Rice riboSNitch analysis: Collect the sequence data to be run in SNPfold
#
# Author: Kobie Kirven
################################################################################

# Goal: Get a file with the reference sequence and the sequence with the
# alternative allele.


# ----- Import modules ----#
import argparse
import json
import pandas as pd
import sys
import pyfaidx


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


# -- main --#

if __name__ == "__main__":

    # ----- Parse arguments ----#
    parser = argparse.ArgumentParser(
        description="Extract sequences surrounding variants"
    )
    parser.add_argument("--vcf", dest="vcf", help="VCF File")
    parser.add_argument("--ref-genome", dest="ref", help="Reference Genome")
    parser.add_argument("--gffread", dest="gffread", help="Gffread Table")
    parser.add_argument("--flank", dest="flank", help="SNP flanking length")
    parser.add_argument("--o", dest="output", help="Output File")
    args = parser.parse_args()

    # Open the output files
    fn = open(args.output, "w")
    no_match = open(args.output[:-4] + "_no_match.txt", "w")

    # Read in the file with the SNPEff predictions
    predictions = pd.read_csv(args.vcf, sep="\t", header=0)
    predictions = predictions.dropna()

    # Get the feature ID
    feature = "Feature"

    # Opening JSON file
    f = open(args.gffread)

    # returns JSON object as
    # a dictionary
    transcript_data = json.load(f)

    for i in range(len(predictions)):
        # Check to make sure it is not an INDEL
        if (
            len(predictions.iloc[i]["REF_ALLELE"]) > 1
            or len(predictions.iloc[i]["Allele"]) > 1
            or predictions.iloc[i]["Allele"] == "-"
            or predictions.iloc[i]["REF_ALLELE"] == "-"
        ):
            continue

        # Get the start and stop positions of the transcript
        start = transcript_data[predictions.iloc[i][feature]][1]
        end = transcript_data[predictions.iloc[i][feature]][2]

        chrom = predictions.iloc[i]["#Location"].split(":")[0]
        position = int(predictions.iloc[i]["#Location"].split(":")[1])

        # Check to make sure it is not within a certain distance from the 5' and 3' ends of the transcript
        if five_prime_test(position, start, args.flank) and three_prime_test(
            position, end, args.flank
        ):

            if len(predictions.iloc[i]["REF_ALLELE"]) > 1:
                if not five_prime_test(
                    (position + len(predictions.iloc[i]["REF_ALLELE"])),
                    start,
                    args.flank,
                ) and three_prime_test(
                    position + len(predictions.iloc[i]["REF_ALLELE"]),
                    end,
                    args.flank,
                ):
                    continue

            sequence = pyfaidx.Fasta(args.ref)[chrom][start - 1 : end].seq

            # Complement the reference and alternative alleles if the transcript is on the negative strand
            if str(predictions.iloc[i]["STRAND"]) == "-1":
                sequence = compelement_dna(sequence)
                reference = compelement_dna(predictions.iloc[i]["REF_ALLELE"])
                alternative = compelement_dna(predictions.iloc[i]["Allele"])

            elif str(predictions.iloc[i]["STRAND"]) == "1":
                reference = predictions.iloc[i]["REF_ALLELE"]
                alternative = predictions.iloc[i]["Allele"]

            # Get the nucleotides at the location of the variant
            else:
                print(type(predictions.iloc[i]["STRAND"]))

            snp_seq = sequence[
                (position - start) : ((position - start) + (len(reference)))
            ]

            # Get the flanking sequence
            flank_left = sequence[
                (position - start) - int(args.flank) : (position - start)
            ]
            flank_right = sequence[
                ((position - start) + len(reference)) : (
                    (position - start) + len(reference)
                )
                + int(args.flank)
            ]

            # Check to see if the sequence in the reference genome matches the reference allele or the alternative allele
            # If it matches the reference, then we do not change anything. If it matches the alternative, then we reverse
            # the reference and alternative alleles

            # Check to see if the SNP matches the alternative allele
            if snp_seq == alternative:
                ref = alternative
                alt = reference
                flank = flank_left + ref + flank_right
                fn.write(
                    f'{chrom}\t{position}\t{position}\t{ref}\t{alt}\t{flank_left}\t{flank_right}\t{predictions.iloc[i][feature]}\tMATCHED_ALT\t{predictions.iloc[i]["Consequence"]}\t{predictions.iloc[i]["STRAND"]}\n'
                )

            # Check to see if the SNP matches the reference allele
            elif snp_seq == reference:
                ref = reference
                alt = alternative
                flank = flank_left + ref + flank_right
                fn.write(
                    f'{chrom}\t{position}\t{position}\t{ref}\t{alt}\t{flank_left}\t{flank_right}\t{predictions.iloc[i][feature]}\tMATCHED_REF\t{predictions.iloc[i]["Consequence"]}\t{predictions.iloc[i]["STRAND"]}\n'
                )

            # If the SNP does not match the reference or alternative allele, then we skip it
            else:
                ref = alternative
                alt = reference
                no_match.write(
                    f"{chrom}\t{position}\t{position}\t{ref}\t{alt}\t{flank_left}\t{flank_right}\t{predictions.iloc[i][feature]}\n"
                )

    fn.close()
