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
import json 

# ----- Parse arguments ----#
parser = argparse.ArgumentParser(description="Extract sequences surrounding variants")
parser.add_argument("--vcf", dest="vcf", help="VCF File")
parser.add_argument("--database", dest="database", help="gffutils database")
parser.add_argument("--ref-genome", dest="ref", help="Reference Genome")
parser.add_argument("--flank", dest="flank", help="SNP flanking length")
parser.add_argument("--o", dest="output", help="Output File")
parser.add_argument("--utr-file", dest="utr", help="UTR File")
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
utr_file = open(args.utr, "w")
no_match = open(args.output[:-4] + "_no_match.txt", "w")

# Read in the file with the SNPEff predictions
predictions = pd.read_csv(args.vcf, sep="\t", header=0)
predictions = predictions.dropna()

# Get the feature ID
feature = "ANN[*].FEATUREID"

for i in range(len(predictions)):
    # Check to make sure it is an MNV
    if (
        len(predictions.iloc[i]["REF"]) > 1
        and len(predictions.iloc[i]["ALT"]) > 1
        and len(predictions.iloc[i]["REF"]) == len(predictions.iloc[i]["ALT"])
    ):
        continue

    # Get the start and stop positions of the transcript
    start = db[predictions.iloc[i][feature]].start
    end = db[predictions.iloc[i][feature]].end

    # Get the UTR information
    five_prime_utr = list(db.children(predictions.iloc[i][feature], featuretype="five_prime_UTR"))
    three_prime_utr = list(db.children(predictions.iloc[i][feature], featuretype="three_prime_UTR"))

    # Check to make sure there is a 5' and 3' UTR
    if len(five_prime_utr) == 0:
        five_prime_start = ['NA']
        five_prime_end = ['NA']
    else:
        five_prime_start = five_prime_utr[0].start
        five_prime_end = five_prime_utr[0].end

    if len(three_prime_utr) == 0:
        three_prime_starts = ['NA']
        three_prime_end = ['NA']
    else:
        three_prime_start = three_prime_utr[0].start
        three_prime_end = three_prime_utr[0].end


    # Get the locations of introns
    introns = list(db.children(predictions.iloc[i][feature], featuretype="intron"))
    
    # Get the locations of exons
    exons = list(db.children(predictions.iloc[i][feature], featuretype="exon"))
    
    # Write all of the location information to the UTR file in json format
    utr_file.write(
        json.dumps(
            {
                "feature": predictions.iloc[i][feature],
                "five_prime_start": five_prime_start,
                "five_prime_end": five_prime_end,
                "three_prime_start": three_prime_start,
                "three_prime_end": three_prime_end,
                "intron_starts": [intron.start for intron in introns],
                "intron_ends": [intron.end for intron in introns],
                "exon_starts": [exon.start for exon in exons],
                "exon_ends": [exon.end for exon in exons],
            }
    ))
    

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

        sequence = db[predictions.iloc[i][feature]].sequence(
            args.ref, use_strand=False
        )

        # Swap the reference and alternative alleles if the transcript is on the negative strand
        if db[predictions.iloc[i][feature]].strand == "-":
            sequence = compelement_dna(sequence)
            reference = compelement_dna(predictions.iloc[i]["ALT"])
            alternative = compelement_dna(predictions.iloc[i]["REF"])

        elif db[predictions.iloc[i][feature]].strand == "+":
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
        
        # Check to see if the SNP matches the alternative allele
        if snp_seq == alternative:
            ref = alternative
            alt = reference
            flank = flank_left + ref + flank_right
            fn.write(
                f'{predictions.iloc[i]["CHROM"]}\t{predictions.iloc[i]["POS"]}\t{ref}\t{alt}\t{flank_left}\t{flank_right}\t{predictions.iloc[i][feature]}\tMATCHED_ALT\t{db[predictions.iloc[i][feature]].featuretype}\t{db[predictions.iloc[i][feature]].strand}\t{predictions.iloc[i]["ANN[*].EFFECT"]}\n'
            )

        # Check to see if the SNP matches the reference allele
        elif snp_seq == reference:
            ref = reference
            alt = alternative
            flank = flank_left + ref + flank_right
            fn.write(
                f'{predictions.iloc[i]["CHROM"]}\t{predictions.iloc[i]["POS"]}\t{ref}\t{alt}\t{flank_left}\t{flank_right}\t{predictions.iloc[i][feature]}\tMATCHED_REF\t{db[predictions.iloc[i][feature]].featuretype}\t{db[predictions.iloc[i][feature]].strand}\t{predictions.iloc[i]["ANN[*].EFFECT"]}\n'
            )

        # If the SNP does not match the reference or alternative allele, then we skip it
        else:
            no_match.write(
                f'{predictions.iloc[i][feature]}\t{predictions.iloc[i]["POS"]}\t{flank}\t{predictions.iloc[i]["REF"]}\t{predictions.iloc[i]["ALT"]}\t{db[predictions.iloc[i][feature]].strand}\t{predictions.iloc[i]["ANN[*].EFFECT"]}\n'
            )

fn.close()
utr_file.close()