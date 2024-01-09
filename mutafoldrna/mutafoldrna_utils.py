#####################################################################
# Functions for the SPARCS command line tool
#####################################################################

import os

# Functions for printing to the command line in different colors
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))
def prCyan(skk): print("\033[96m {}\033[00m" .format(skk))
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))

def config_builder(output_file, working_directory, vcf_file, gff_file, 
                   ref_genome, output_dir, flank, chunks, temperature,
                   ribo_tool, structure_tool, riprap_min_window, temp_step, spliced, canonical, top_n_percent, subset_size,
                   null_only, rbsn_only):
    '''
    Generates a config file for running the MutaFoldRNA pipeline
    '''
    output = open(output_file, "w")
    header = '''#=======================================================================
#                       Configuration File
# ---------------------------------------------------------------------
# This file contains all of the user-specified parameters for running 
# the MutaFoldRNA pipeline.
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
# gff_file - Gene model (must be in GFF format)
#############################################################\n''')
    output.write(f"gff_file: {gff_file}\n\n")

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
# spliced - Boolen whether to use the spliced or unspliced transcripts
# for riboSNitch prediction 
#############################################################\n''')
    output.write(f"spliced: {spliced}\n\n")

    output.write('''#############################################################
# Canonical - Boolen whether to use the canonical form of the transcripts
# for riboSNitch prediction 
#############################################################\n''')
    output.write(f"canonical: {canonical}\n\n")

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
                 # subset_size - Number of variants to use for the null model )
#############################################################''')
    output.write(f"\nsubset_size: {subset_size}\n\n")

    output.write('''#############################################################
# shuffle_null - Boolen whether to shuffle the REF and ALT alleles
#                for the null model
#############################################################''')
    output.write(f"\nshuffle_null: {shuffle_null}\n\n")
    
    output.write('''#############################################################
# null_only - Boolen whether to only run the null model
#############################################################''')
    output.write(f"\nnull_only: {null_only}\n\n")

    output.write('''#############################################################
# rbsn_only - Boolen whether to only run the riboSNitch model
#############################################################''')
    output.write(f"\nrbsn_only: {rbsn_only}\n\n")

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

    output.write('''#############################################################
# top_n_percent: The top n percent to define as riboSNitches
#                (default = 0.05)
#############################################################''')
    output.write(f"\ntop_n_percent: {top_n_percent}\n\n")

    output.write('''# -- ADVANCED PARAMETERS -- #
#############################################################
# riprap_min_window: Minimum window size for RipRap
#############################################################''')
    output.write(f"\nriprap_min_window: {riprap_min_window}\n\n")
    
    output.close()


# Create a bash script to run the SPARCS pipeline
def bash_builder(output_file, cores, working_directory, singularity_prefix=None, singularity_bind=None,  cluster=False, cluster_info=None, jobs=None):
    '''
    Generates a bash script for running the MutaFoldRNA pipeline
    '''
    output = open(output_file, "w")
    header = '''#!/bin/bash

# This script runs the MutaFoldRNA pipeline\n\n'''

    output.write(header)
    output.write("echo 'Running MutaFoldRNA...'\n\n")

    # Start building the snakemake command:
    if singularity_bind is not None:
        command = f"snakemake -s workflow/mutafoldrna.smk --cores {cores} --use-singularity --singularity-args ' -B {singularity_bind}' --latency-wait 200 --rerun-incomplete "
    else:
        command = f"snakemake -s workflow/mutafoldrna.smk --cores {cores} --use-singularity --singularity-args ' -B {os.path.abspath(working_directory)}' --latency-wait 200 --rerun-incomplete "
    
    if singularity_prefix is not None:
        command += f" --singularity-prefix {singularity_prefix} "
    
    if cluster:
        command += f" --cluster '{cluster_info}' "
        command += f" -j {jobs} "

    # Write the command to the bash script
    output.write(command + "\n\n")
    output.close()