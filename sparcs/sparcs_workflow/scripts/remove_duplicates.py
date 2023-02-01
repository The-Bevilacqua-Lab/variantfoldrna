import argparse
import pandas as pd

parser = argparse.ArgumentParser(description="Break up VCF file")
parser.add_argument("-i", dest="input", help="input file")
parser.add_argument("-o", dest="output", help="output file")

args = parser.parse_args()

data = pd.read_csv(args.input, header=None, sep="\t")
data = data.drop_duplicates()
data.to_csv(args.output, sep="\t", header=None)
