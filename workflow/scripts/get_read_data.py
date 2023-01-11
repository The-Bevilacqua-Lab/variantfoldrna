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
import gffutils
import pandas as pd

parser = argparse.ArgumentParser(description="Extract sequences surrounding variants")
parser.add_argument("--vcf", dest="vcf", help="VCF File")
parser.add_argument("--database", dest="database", help="gffutils database")
parser.add_argument("--ref-genome", dest="ref", help="Reference Genome")
parser.add_argument("--flank", dest="flank", help="SNP flanking length")
parser.add_argument("--o", dest="output", help="Output File")
args = parser.parse_args()

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
    return "".join([complement[base] for base in dna])


def test_five_prime(pos, start, flank):
    """
    Test to make sure the SNP is far enough away from the
    5' end of the transcript
    """
    if int(pos) > (int(start) + (int(flank) - 1)):
        return True
    else:
        return False


def test_three_prime(pos, end, flank):
    """
    Test to make sure the SNP is far enough away from the
    3' end of the transcript
    """
    if int(pos) < (int(end) - (int(flank) - 1)):
        return True
    else:
        return False


# load the GFFUtils database
db = gffutils.FeatureDB(args.database, keep_order=True)

# Open the output files
fn = open(args.output, "w")
no_match = open(args.output[:-4] + "_no_match.txt", "w")

# Read in the file with the SNPEff predictions
predictions = pd.read_csv(args.vcf, sep="\t", header=0)
predictions = predictions.dropna()

for i in range(len(predictions)):
    # Check to make sure it is an MNV
    if (
        len(predictions.iloc[i]["REF"]) > 1
        and len(predictions.iloc[i]["ALT"]) > 1
        and len(predictions.iloc[i]["REF"]) == len(predictions.iloc[i]["ALT"])
    ):
        continue

    # Get the start and stop positions of the transcript
    start = db[predictions.iloc[i]["ANN[*].GENEID"]].start
    end = db[predictions.iloc[i]["ANN[*].GENEID"]].end

    # Check to make sure it is not within a certain distance from the 5' and 3' ends of the transcript
    if test_five_prime(
        predictions.iloc[i]["POS"], start, args.flank
    ) and test_three_prime(predictions.iloc[i]["POS"], end, args.flank):

        if len(predictions.iloc[i]["REF"]) > 1:
            if not test_five_prime(
                (predictions.iloc[i]["POS"] + len(predictions.iloc[i]["REF"])),
                start,
                args.flank,
            ) and test_three_prime(
                predictions.iloc[i]["POS"] + len(predictions.iloc[i]["REF"]),
                end,
                args.flank,
            ):
                continue

        sequence = db[predictions.iloc[i]["ANN[*].GENEID"]].sequence(
            args.ref, use_strand=False
        )

        # Swap the reference and alternative alleles if the transcript is on the negative strand
        if db[predictions.iloc[i]["ANN[*].GENEID"]].strand == "-":
            sequence = compelement_dna(sequence)
            reference = compelement_dna(predictions.iloc[i]["ALT"])
            alternative = compelement_dna(predictions.iloc[i]["REF"])

        elif db[predictions.iloc[i]["ANN[*].GENEID"]].strand == "+":
            reference = predictions.iloc[i]["REF"]
            alternative = predictions.iloc[i]["ALT"]

        # Get the nucleotides at the location of the variant
        snp_seq = sequence[
            (predictions.iloc[i]["POS"] - start) : (
                (predictions.iloc[i]["POS"] - start) + (len(reference))
            )
        ]

        # Get the flanking sequence
        flank_left = sequence[
            (predictions.iloc[i]["POS"] - start)
            - int(args.flank) : (predictions.iloc[i]["POS"] - start)
        ]
        flank_right = sequence[
            ((predictions.iloc[i]["POS"] - start) + len(reference)) : (
                (predictions.iloc[i]["POS"] - start) + len(reference)
            )
            + int(args.flank)
        ]

        # Check to see if the sequence in the reference genome matches the reference allele or the alternative allele
        # If it matches the reference, then we do not change anything. If it matches the alternative, then we reverse
        # the reference and alternative alleles
        if len(predictions.iloc[i]["REF"]) > 1 or len(predictions.iloc[i]["ALT"]) > 1:
            ref = reference
            alt = alternative
            flank = flank_left + ref + flank_right
            fn.write(
                f'{predictions.iloc[i]["CHROM"]}\t{predictions.iloc[i]["POS"]}\t{ref}\t{alt}\t{flank_left}\t{flank_right}\t{predictions.iloc[i]["ANN[*].GENEID"]}\tNA\t{db[predictions.iloc[i]["ANN[*].GENEID"]].featuretype}\t{db[predictions.iloc[i]["ANN[*].GENEID"]].strand}\n'
            )

        elif snp_seq == alternative:
            ref = alternative
            alt = reference
            flank = flank_left + ref + flank_right
            fn.write(
                f'{predictions.iloc[i]["CHROM"]}\t{predictions.iloc[i]["POS"]}\t{ref}\t{alt}\t{flank_left}\t{flank_right}\t{predictions.iloc[i]["ANN[*].GENEID"]}\tMATCHED_ALT\t{db[predictions.iloc[i]["ANN[*].GENEID"]].featuretype}\t{db[predictions.iloc[i]["ANN[*].GENEID"]].strand}\n'
            )

        elif snp_seq == reference:
            ref = reference
            alt = alternative
            flank = flank_left + ref + flank_right
            fn.write(
                f'{predictions.iloc[i]["CHROM"]}\t{predictions.iloc[i]["POS"]}\t{ref}\t{alt}\t{flank_left}\t{flank_right}\t{predictions.iloc[i]["ANN[*].GENEID"]}\tMATCHED_REF\t{db[predictions.iloc[i]["ANN[*].GENEID"]].featuretype}\t{db[predictions.iloc[i]["ANN[*].GENEID"]].strand}\n'
            )

        else:
            no_match.write(
                f'{predictions.iloc[i]["ANN[*].GENEID"]}\t{predictions.iloc[i]["POS"]}\t{flank}\t{predictions.iloc[i]["REF"]}\t{predictions.iloc[i]["ALT"]}\t{db[predictions.iloc[i]["ANN[*].GENEID"]].strand}\n'
            )

fn.close()
