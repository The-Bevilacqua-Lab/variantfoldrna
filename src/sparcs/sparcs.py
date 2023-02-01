###########################################################################
# Main file for running the SPARCS pipeline. This acts a wrapper that
# will automactically create everythigng needed to run the Snakemake
# pieline without having to worry about the details.
#
# Author: Kobie Kirven (kjk617@psu.edu)
# Assmann Lab, The Pennsylvania State University
#
###########################################################################

# Imports
import argparse
import os
import subprocess
import sys
from .sparcs_utils import *


def main():

    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="Run the SPARCS pipeline")
    parser.add_argument(
        "--vcf",
        dest="vcf",
        help="Path to VCF file (If not specified, will check the current directory",
    )
    parser.add_argument(
        "--gtf",
        dest="gtf",
        help="Path to GTF file (If not specified, will check the current directory",
    )
    parser.add_argument(
        "--fasta",
        dest="fasta",
        help="Path to FASTA file (If not specified, will check the current directory",
    )
    parser.add_argument(
        "--out-dir",
        dest="out",
        help="Path to output directory (If not specified, will create a new directory named 'sparcs_output' in the current directory",
        default="sparcs_pipeline",
    )
    parser.add_argument(
        "--chunks",
        dest="chunks",
        help="Number of chunks to split the VCF file into (Default: 10)",
        default=10,
    )
    parser.add_argument(
        "--cores", dest="cores", help="Number of cores to use (Default: 1)", default=1
    )
    parser.add_argument(
        "--structure-pred-tool",
        dest="structure_pred_tool",
        help="Structure prediction tool to use (RNAfold or RNAstructure, Default: RNAfold)",
    )
    parser.add_argument(
        "--ribosnitch-tool",
        dest="ribosnitch_tool",
        help="RiboSNitch prediction tool to use (SNPfold or Riprap, Default: SNPfold)",
    )
    parser.add_argument(
        "--ribosnitch-flank",
        dest="ribosnitch_flank",
        help="Flanking length for RiboSNitch prediction (Default: 40)",
        default=40,
    )
    parser.add_argument(
        "--temperature",
        dest="temperature",
        help="Temperature for structural prediction (Default: 37.0)",
        default=37.0,
    )
    parser.add_argument(
        "--minwindow",
        dest="minwindow",
        help="Minimum window size for Riprap (Default: 3)",
        default=3,
    )
    args = parser.parse_args()

    # Get the location of where this file is stored
    file_location = os.path.dirname(os.path.realpath(__file__))

    # Get the location of where this file is being ran
    location = os.getcwd()

    # Get the location of the output directory
    if args.out:
        output_dir = args.out
    else:
        output_dir = os.path.join(location, "sparcs_pipeline")
        prYellow(
            "Output directory not specified, so will create a new directory named 'sparcs_pipeline' in the current directory"
        )

    # Try to create the output directory
    try:
        os.mkdir(output_dir)
    except:
        raise Exception("Could not create the output directory")

    # Copy all of the relevant files to the output directory
    # Copy the scripts directory
    subprocess.call("cp -r {}/scripts {}".format(file_location, output_dir), shell=True)

    # Copy the Snakefile
    subprocess.call(
        "cp {}/sparcs.rules {}".format(file_location, output_dir), shell=True
    )

    # Copy the envs directory
    subprocess.call("cp -r {}/envs {}".format(file_location, output_dir), shell=True)

    # Copy the rules directory
    subprocess.call("cp -r {}/rules {}".format(file_location, output_dir), shell=True)

    # Check to to see if the user has a VCF file, a GTF file, and a FASTA file in the current directory
    inputted_files = {"VCF": None, "GTF": None, "FASTA": None}
    if args.vcf:
        inputted_files["VCF"] = args.vcf
    if args.gtf:
        inputted_files["GTF"] = args.gtf
    if args.fasta:
        inputted_files["FASTA"] = args.fasta

    # The user has specified at least one of the files, so we will
    # let the user know what files they have specified
    if len([x for x in inputted_files.values() if x != None]) > 0:
        prGreen("Specified files inclde: ")
        for file_type, file_path in inputted_files.items():
            if file_path:
                prGreen("   - {}: {}".format(file_type, file_path))

    # The user did not specify all of the files, so we will check to see
    # if the files are in the current directory
    if len([x for x in inputted_files.values() if x != None]) != 3:
        prGreen("\n")
        prGreen("Checking for files in the current directory...")

        files_found = []
        for file_type, file_path in inputted_files.items():
            if file_path == None:
                for file in os.listdir(location):
                    if file.endswith(file_type.lower()):
                        inputted_files[file_type] = os.path.join(location, file)
                        files_found.append(
                            "   - {}: {}".format(file_type, inputted_files[file_type])
                        )
                        break
        if len(files_found) == 0:
            prYellow(
                "Warning: No files found in the current directory! You will need to manually edit the config.yaml file to specify the paths to the files."
            )

        else:
            prGreen("Found the following files in the current directory:")
            for file_found in files_found:
                prGreen(file_found)

    # Create the config.yaml file
    if inputted_files["VCF"] == None:
        vcf_file = "NA"
    else:
        vcf_file = inputted_files["VCF"]

    if inputted_files["GTF"] == None:
        gtf_file = "NA"
    else:
        gtf_file = inputted_files["GTF"]

    if inputted_files["FASTA"] == None:
        ref_genome = "NA"
    else:
        ref_genome = inputted_files["FASTA"]

    if output_dir.endswith("/"):
        output_dir = output_dir[:-1]

    prGreen("\n")
    prGreen("Generating the necessary files for the SPARCS pipeline...")

    config_builder(
        f"{file_location}/config.yaml",
        output_dir + "/sparcs_output",
        vcf_file,
        gtf_file,
        ref_genome,
        output_dir,
        args.ribosnitch_flank,
        args.chunks,
        args.temperature,
        args.ribosnitch_tool,
        args.structure_pred_tool,
        args.minwindow,
    )

    bash_builder(f"{output_dir}/sparcs.sh", args.cores)

    prGreen("All Done!\n")
    prCyan("To run the SPARCS pipeline, run the following commands:")
    prCyan("   cd {}".format(output_dir))
    prCyan("   snakemake --use-conda --cores 1")
    prCyan("\n Thank you for using SPARCS!")


if __name__ == "__main__":
    main()
