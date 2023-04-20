#####################################################################
# Functions for the SPARCS command line tool
#####################################################################

# Functions for printing to the command line in different colors
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))
def prCyan(skk): print("\033[96m {}\033[00m" .format(skk))
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))

def config_builder(output_file, working_directory, vcf_file, gtf_file, 
                   ref_genome, output_dir, flank, chunks, temperature,
                   ribo_tool, structure_tool, riprap_min_window, temp_step, scramble):
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
# temp_step - Temperature step for RNA structure prediction
#############################################################''')
    output.write(f"\ntemp_step: {temp_step}\n\n")

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

    output.write('''
##################################################################
# scramble: Scramble the RNA sequence before riboSNitch prediction
###################################################################''')
    output.write(f"\nscramble: {scramble}\n\n")
    
    output.close()


# Create a bash script to run the SPARCS pipeline
def bash_builder(output_file, cores):
    '''
    Generates a bash script for running the SPARCS pipeline
    '''
    output = open(output_file, "w")
    header = '''#!/bin/bash

# This script runs the SPARCS pipeline\n\n'''

    output.write(header)
    output.write("echo 'Running SPARCS...'\n\n")
    output.write(f"snakemake -s workflow/sparcs.smk --cores {cores} --use-conda --conda-frontend conda\n")
    output.close()

