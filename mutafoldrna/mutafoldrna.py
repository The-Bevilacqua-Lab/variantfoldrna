###########################################################################
# Main file for running the mutafoldrna pipeline. This acts a wrapper that
# will automatically create everything needed to run the Snakemake
# pipeline without having to worry about the details.
#
# Author: Kobie Kirven (kjk617@psu.edu)
# Assmann Lab, The Pennsylvania State University
#
###########################################################################

# -- Imports -- #
import argparse
import os
import subprocess
import sys
import shutil
try:
    from .mutafoldrna_utils import *
except:
    from mutafoldrna_utils import *


def main():

    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="Run the mutafoldrna pipeline")
    parser.add_argument(
        "--vcf",
        dest="vcf",
        help="Absolute ath to VCF file (If not specified, will check the current directory",
        required=True,
    )
    parser.add_argument(
        "--gff",
        dest="gff",
        help="Absolute path to GFF file (If not specified, will check the current directory",
        required=True,
    )
    parser.add_argument(
        "--ref-genome",
        dest="fasta",
        help="Absolute path to the reference genome file (If not specified, will check the current directory",
        required=True,
    )
    parser.add_argument(
        "--out-dir",
        dest="out",
        help="Path to output directory (If not specified, will create a new directory named 'mutafoldrna_output' in the current directory",
        default="mutafoldrna_pipeline",
    )
    parser.add_argument(
        "--spliced",
        action='store_true', 
        help='Used the spliced form of transcripts'
        
        )

    parser.add_argument(
        "--canonical",
        action='store_true', 
        help='Used only the canonical transcripts'
        
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
        default = "RNAfold",
    )
    parser.add_argument(
        "--ribosnitch-tool",
        dest="ribosnitch_tool",
        help="RiboSNitch prediction tool to use (SNPfold or Riprap, Default: SNPfold)",
        default = "SNPfold",
    )
    parser.add_argument(
        "--flank",
        dest="ribosnitch_flank",
        help="Flanking length for RiboSNitch prediction (Default: 40)",
        default=40,
    )
    parser.add_argument("--singularity-bind", dest="singularity_bind", help="Path to directory to bind to singularity", default=None)
    parser.add_argument(
        "--temperature",
        dest="temperature",
        help="Temperature for structural prediction (Default: 37.0)",
        default=37.0,
    )
    parser.add_argument(
        "--temp-step",
        dest="temp_step",
        help="Temperature step for structural prediction (Default: 5)",
        default=5,
    )
    parser.add_argument(
        "--minwindow",
        dest="minwindow",
        help="Minimum window size for Riprap (Default: 3)",
        default=3,
    )
    parser.add_argument(
        "--singularity-path",
        dest="singularity",
        help="Path to directory that holds the singularity containers"
    )

    parser.add_argument(
        "--force",
        action='store_true', 
        help='Create the output directory even if it already exists'
        
        )
    
    parser.add_argument(
        "--cluster",
        action='store_true',
        help='flag to indicate that the pipeline will be run on a cluster'
    )

    parser.add_argument(
        "--cluster-info",
        dest="cluster_info",
        help="Info for jobs to be submitted to the cluster. "

    )

    parser.add_argument(
        "--jobs",
        dest="jobs",
        help="Number of jobs to be submitted to the cluster. ",
        default=10
    )

    parser.add_argument(
        "--null-only",
        action='store_true',
        help='Only the riboSNitch predictions for building the null distribution. '
    )

    parser.add_argument(
        "--rbsn-only",
        action='store_true',
        help='Only the riboSNitch predictions, no null distribution. '
    )

    parser.add_argument(
        "--top-n-percent",
        dest="top_n_percent",
        help="The top n percent to define as riboSNitches (default = 0.05)",
        default=0.05
    )

    # Parse the command line arguments
    args = parser.parse_args()

    # Make sure that, if the user inputs RNAsnp, that the flanking length is a multiple of 50, >= 100, and <= 800
    if args.ribosnitch_tool.lower() == "rnasnp":
        if int(args.ribosnitch_flank) < 100 or int(args.ribosnitch_flank) > 800:
            prRed("Error: RNAsnp requires the flanking length to be >= 100 and <= 800")
            sys.exit(1)
        if int(args.ribosnitch_flank) % 50 != 0:
            prRed("Error: RNAsnp requires the flanking length to be a multiple of 50")
            sys.exit(1)

    # Get the location of where this file is stored. We will use this
    # to copy the necessary files to the output directory
    file_location = os.path.dirname(os.path.realpath(__file__))


    # -- output directory -- # 

    # Get the location of where this file is being ran. We will use this to 
    # create the output directory
    location = os.getcwd()
    location = os.path.abspath(location)

    # Get the location of the output directory
    if args.out:
        output_dir = args.out
    else:
        output_dir = os.path.join(location, "mutafoldrna_pipeline")
        prYellow(
            "Output directory not specified, so will create a new directory named 'mutafoldrna_pipeline' in the current directory"
        )

    # Try to create the output directory
    try:
        if args.force:
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
        os.mkdir(output_dir)
    except:
        prRed("Error: Could not create output directory: {}".format(output_dir))
        sys.exit(1)

    # Get the full path of the output directory
    output_dir = os.path.abspath(output_dir)

    # -- end output directory -- #

    # -- Copying files -- #
    # Copy all of the relevant files to the output directory
    # Copy the scripts directory
    try:
        subprocess.call("mkdir {}/workflow".format(output_dir), shell=True)
    except:
        prRed("Error: Could not copy the workflow directory to the output directory")
        sys.exit(1)
    try:
        subprocess.call("cp -r {}/mutafoldrna_workflow/scripts {}/workflow".format(file_location, output_dir), shell=True)
    except:
        prRed("Error: Could not copy the scripts directory to the output directory")
        sys.exit(1)

    # Copy the Snakefile
    try:
        subprocess.call(
            "cp {}/mutafoldrna_workflow/mutafoldrna.smk {}/workflow".format(file_location, output_dir), shell=True
        )
    except:
        prRed("Error: Could not copy the Snakefile to the output directory")
        sys.exit(1)

    # Copy the envs directory
    try:
        subprocess.call("cp -r {}/mutafoldrna_workflow/envs {}/workflow".format(file_location, output_dir), shell=True)

    except:
        prRed("Error: Could not copy the envs directory to the output directory")
        sys.exit(1)

    # Copy the rules directory
    try:
        subprocess.call("cp -r {}/mutafoldrna_workflow/rules {}/workflow".format(file_location, output_dir), shell=True)
    except:
        prRed("Error: Could not copy the rules directory to the output directory")
        sys.exit(1)

    # -- end copying files -- #

    # Check to to see if the user has a VCF file, a GTF file, and a FASTA file in the current directory
    inputted_files = {"VCF": None, "GFF3": None, "FASTA": None}
    if args.vcf:
        inputted_files["VCF"] = os.path.abspath(os.path.expanduser(args.vcf))
    if args.gff:
        inputted_files["GFF3"] = os.path.abspath(os.path.expanduser(args.gff))
    if args.fasta:
        inputted_files["FASTA"] = os.path.abspath(os.path.expanduser(args.fasta))

    # The user has specified at least one of the files, so we will
    # let the user know what files they have specified
    if len([x for x in inputted_files.values() if x != None]) > 0:
        prGreen("Specified files include: ")
        for file_type, file_path in inputted_files.items():
            if file_path:
                prGreen("   - {}: {}".format(file_type, file_path))

    # The user did not specify all of the files, so we will check to see
    # if the files are in the current directory
    if len([x for x in inputted_files.values() if x != None]) != 3:
        prRed("Error: Not all of the necessary files were specified")

    # Create the config.yaml file
    if inputted_files["VCF"] == None:
        vcf_file = "NA"
    else:
        vcf_file = inputted_files["VCF"]

    if inputted_files["GFF3"] == None:
        gff_file = "NA"
    else:
        gff_file = inputted_files["GFF3"]

    if inputted_files["FASTA"] == None:
        ref_genome = "NA"
    else:
        ref_genome = inputted_files["FASTA"]

    if output_dir.endswith("/"):
        output_dir = output_dir[:-1]

    
    # Let the user know that we are generating the necessary files
    prGreen("\n")
    prGreen("Generating the necessary files for the MutaFoldRNA pipeline...")

    if args.null_only:
        null_only = "TRUE"
    else:
        null_only = "FALSE"
    
    if args.rbsn_only:
        rbsn_only = "TRUE"
    else:
        rbsn_only = "FALSE"

    if args.spliced:
        spliced = "TRUE"
    else:
        spliced = "FALSE"
    
    if args.canonical:
        canonical = "TRUE"
    else:
        canonical = "FALSE"

    # Generate the config.yaml file
    config_builder(
        f'{output_dir}/workflow/config.yaml',
        "/".join(output_dir.split("/")[:-1]),
        vcf_file,
        gff_file,
        ref_genome,
        output_dir.split("/")[-1],
        args.ribosnitch_flank,
        args.chunks,
        args.temperature,
        args.ribosnitch_tool,
        args.structure_pred_tool,
        args.minwindow,
        args.temp_step, 
        spliced,
        canonical,
        args.top_n_percent,
        args.null_model_total,
        null_only,
        rbsn_only,
    )

    # Generate the mutafoldrna.sh file
    bash_builder(f"{output_dir}/mutafoldrna.sh", args.cores, args.out, args.singularity, args. singularity_bind, args.cluster, args.cluster_info, args.jobs)
  
    prGreen("All Done!\n")
    prCyan("To run the MutaFoldRNA pipeline, run the following commands:")
    prCyan("   cd {}".format(output_dir))
    prCyan("   bash mutafoldrna.sh\n")
    prCyan("\n Thank you for using MutaFoldRNA!")

if __name__ == "__main__":
    main()
