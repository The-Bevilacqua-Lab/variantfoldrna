===========
File Types
===========

The SPARCS pipeline relies on several different files for the analysis. 
The following is a list of the file types and their purpose.

Input files
-----------
1. Reference Genome (FASTA) - The reference genome holds the sequence
   of the genome of interest. This file is used to get the sequences of 
   the genes of interest. 

2. Gene Annotation (GTF) - The gene annotation file holds the locations 
   of the genes in the genome. This file is used to get the locations 
   of the start and stop positions of the genes of interest. 

3. Variant File (VCF) - The variant file holds the variants that are
   found in the sample. This file is used to get the locations of the
   variants of interest.


Config File
-----------
The config file holds the paths to all of the files that are used in the
pipeline as well as all of the pertinent parameters. The config file is
located in the workflow directory and is named config.yaml. You will need
to edit this file to include the paths to the files that you are using
as well as the parameters that you would like to use.