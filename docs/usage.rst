=============
Usage
=============

Command line usage:

.. code:: bash
    
    sparcs -h 


.. list-table::
   :widths: 25 25
   :header-rows: 1

   * - Parameter
     - Description
   * - ``--vcf``
     - Absolute path to the VCF file 
   * - ``--gtf``
     - Absolute path to the GTF/GFF file 
   * - ``--ref``
     - Absolute path to the reference genome in FASTA format
   * - ``--out-dir``
     - Absolute path to the output directory
   * - ``--chunks``
     - Number of chunks to split the VCF file into for parallel processing
   * - ``--cores`` 
     - Number of cores to use for parallel processing
   * - ``--structure-pred-tool``
     - Structure prediction tool to use (RNAfold or RNAstructure, Default: RNAfold)
   * - ``--ribosnitch-tool``
     - RiboSNitch prediction tool to use (SNPfold or Riprap, Default: SNPfold)
   * - ``--ribosnitch-flank``
     - Flanking length for RiboSNitch prediction (Default: 40)
   * - ``--ribosnitch_prediction_tool``
     - Tool to use for riboSNitch prediction. Options are ``SNPfold`` and ``RipRap``
   * - ``--temperature``
     - Temperature for structural prediction (Default: 37.0) 
   * - ``--minwindow``
     - Minimum window size for RipRap