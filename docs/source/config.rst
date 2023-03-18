Config File
--------------------------------------------------------------

The config file is a convenient way to hold all of the parameters for 
running the SPARCS pipeline. These parameters are automaticly filled in 
when running the ``sparcs`` command, but you can also edit the config file
directly. The config file is located at ``workflow/config.yaml`` inside of the ``SPARCS`` output directory.

.. list-table::
   :widths: 25 25
   :header-rows: 1

   * - Config Parameter
     - Description
   * - working_directory
     - Directory where all the output files will be written
   * - vcf_file
     - Absolute path to the VCF file
   * - gtf_file
     - Absolute path to the GTF/GFF file 
   * - ref_genome
     - Absolute path to the reference genome in FASTA format
   * - name
     - Name for file prefixes
   * - output_name
     - Name of the output directory 
   * - flank_len
     - Number of nucleotides on either side of the SNP for riboSNitch prediction 
   * - chunks
     - Number of chunks to split the VCF file into for parallel processing
   * - temperature 
     - Temperature for prediction of RNA secondary structure (in degrees Celsius)
   * - ribosnitch_prediction_tool
     - Tool to use for riboSNitch prediction. Options are ``SNPfold`` and ``RipRap``
   * - structure_prediction_tool
     - Tool to use for RNA secondary structure prediction. Options are ``RNAfold`` and ``RNAstructure`` 
   * - riprap_min_window
     - Minimum window size for RipRap 