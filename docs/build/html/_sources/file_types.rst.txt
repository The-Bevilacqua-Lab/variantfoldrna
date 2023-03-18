======================
Input and Output Files
======================

The SPARCS pipeline relies on several different files for the analysis. 
The following is a list of the file types and their purposes

Input files
-----------
SPARCS can handle gzipped files or files that are not compressed as input.  

1. Reference Genome (FASTA) - The reference genome holds the sequence
   of the genome of interest. This file is used to get the sequences of 
   the genes of interest. 

2. Gene Annotation (GTF/GFF) - The gene annotation file holds the locations 
   of the genes in the genome. This file is used to get the locations 
   of the start and stop positions of the genes of interest. 

3. Variant File (VCF) - The variant file holds the variants that are
   found in the sample. This file is used to get the locations of the
   variants of interest.


Output files:
-------------
The main output of the SPARCS pipeline is a file that contains all 
of the riboSNitch predictions for the variants of interest. This file 
is located inside of the ``results/ribosnitch_predictions`` directory
inside of the output directory. The file name is ``combined_ribosnitch_prediction_{TEMPERATURE}.txt`` 
where ``{TEMPERATURE}`` is the temperature that was used for the analysis.