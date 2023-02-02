##############################################################################
# Helper functions for running snakemake in tests
# 
# Author: Kobie Kirven
##############################################################################

# -- imports --
import subprocess
import sys
import os 

def prCyan(skk):
    print("\033[96m {}\033[00m".format(skk))

def run_snakemake(
    config_args="conda",
    verbose=False,
    snakefile="Snakefile",
    outdir=None,
    extra_args=[],
):
    """
    Run snakemake with the given configfile, and return the exit code.
    """

    # basic command
    cmd = ["snakemake", "-s", snakefile]

    cmd += ["--use-conda", "--conda-frontend", "conda"]

    # snakemake sometimes seems to want a default -j; set it to 1 for now.
    # can overridden later on command line.
    cmd += ["-j", "1"]

    # add rest of snakemake arguments
    cmd += list(extra_args)

    try:
        #subprocess.check_call(cmd, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print(f"Error in snakemake invocation: {e}", file=sys.stderr)
        return e.returncode

    return 0

def config_builder(output_file, working_directory, vcf_file, gtf_file, 
                   ref_genome, output_dir, flank, chunks, temperature,
                   ribo_tool, structure_tool, riprap_min_window):
    '''
    Generates a config file for running the SPARCS pipeline
    '''
    output = open(output_file, "w")
    header = '''#=======================================================================
#                       Configuration File
# ---------------------------------------------------------------------
# This file contains all of the user-specified parameters for running 
# the SPARCS pipeline.
#  
# Replace each of the values to the right of the colon for each 
# parameters with the appropriate value.
# 
#   ---- Note: File paths must be absolute file paths! ----
#=======================================================================

# -- PATHS -- #
#############################################################
# Working_directory - directory to store the output folders  
#############################################################\n'''
    output.write(header)
    output.write(f"working_directory: {working_directory}\n\n")

    output.write('''# -- INPUT FILES -- # 
#############################################################
# vcf_file - Variants file 
#############################################################\n''')
    output.write(f"vcf_file: {vcf_file}\n\n")

    output.write('''#############################################################
# gtf_file - Gene model (must be in GTF format)
#############################################################\n''')
    output.write(f"gtf_file: {gtf_file}\n\n")

    output.write('''#############################################################
# ref_genome - Reference genome in FASTA format 
#############################################################\n''')
    output.write(f"ref_genome: {ref_genome}\n\n")

    output.write('''\n# -- PARAMETERS -- #
#############################################################
# Name - File prefix name 
#############################################################''')
    output.write(f"\nname: {vcf_file.split('/')[-1].split('.')[0]}\n\n")

    output.write('''#############################################################
# out_name - Name of the output directory
#############################################################\n''')
    output.write(f"out_name: {output_dir}\n\n")

    output.write('''#############################################################
# flank_len - number of nucleotides on either side of 
#                the SNP for riboSNitch prediciton 
#############################################################\n''')
    output.write(f"flank_len: {flank}\n\n")

    output.write('''#############################################################
# Chunks - The number of splits of the input files 
#############################################################\n''')
    output.write(f"chunks: {chunks}\n\n")

    output.write('''#############################################################
# temperature - Temperature for RNA structure prediction
#############################################################''')
    output.write(f"\ntemperature: {temperature}\n\n")

    output.write('''#############################################################
# ribosnitch_prediction_tool: Tool to use for predicting
#                             riboSNitches 
#                            (SNPfold or Riprap)  
#############################################################''')
    output.write(f"\nribosnitch_prediction_tool: {ribo_tool}\n\n")

    output.write('''#############################################################
# structure_prediction_tool: Tool to use for predicting the RNA
#                  structural ensembles (RNAfold or RNAplfold)
#############################################################''')
    output.write(f"\nstructure_prediction_tool: {structure_tool}\n\n")

    output.write('''# -- ADVANCED PARAMETERS -- #
#############################################################
# riprap_min_window: Minimum window size for RipRap
#############################################################''')
    output.write(f"\nriprap_min_window: {riprap_min_window}\n\n")
    output.close()


def add_workflow():
    workflow_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    workflow_path = "/".join(workflow_path.split("/"))

    # Make sure that we have the pipeline in our current directory for testing
    if not os.path.exists(f"{workflow_path}/tests/workflow"):
        try:
            os.system(f" rm -rf {workflow_path}/tests/sparcs_workflow")
        except:
            pass
        os.system(f"cp -r {workflow_path}/sparcs/sparcs_workflow {workflow_path}/tests && mv {workflow_path}/tests/sparcs_workflow {workflow_path}/tests/workflow")
    else:
        os.system("rm -rf {workflow_path}/tests/workflow")
        os.system(f" rm -rf {workflow_path}/tests/sparcs_workflow")
        os.system(f"cp -r {workflow_path}/sparcs/sparcs_workflow {workflow_path}/tests && mv {workflow_path}/tests/sparcs_workflow {workflow_path}/tests/workflow")

def remove_workflow():
    workflow_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    workflow_path = "/".join(workflow_path.split("/"))

    # Remove the pipeline from our current directory
    try:
        os.system(f"rm -rf {workflow_path}/tests/workflow")
    except:
        pass

    