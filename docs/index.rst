.. currentmodule:: SPARCS

.. figure::  /img/SPARCS_logo.png
   :align: center
   :width: 40%


:mod:`SPARCS` is a `snakemake <https://snakemake.readthedocs.io/en/stable/>`_ pipeline for the transcriptome-wide
prediction of riboSNitches.The SPARCS pipeline makes it easy to predict the effects of SNPs on RNA secondary structure.

Features
--------
- Automatic dependency management
- Ability to utilize custom gene models

.. toctree::
   :caption: Documentation
   :maxdepth: -1

   installation
   usage
   file_types
   config
   

.. toctree::
    :maxdepth: -1
    :caption: Guides

    examples

If using SPARCS, please be sure to cite all relevant papers:
  - Cingolani, Pablo. "Variant annotation and functional prediction: SnpEff." Variant Calling: Methods and Protocols. New York, NY: Springer US, 2012. 289-314.
  - Halvorsen, Matthew, et al. "Disease-associated mutations that alter the RNA structural ensemble." PLoS genetics 6.8 (2010): e1001074.
  - Lin, Jianan, et al. "Identification and analysis of RNA structural disruptions induced by single nucleotide variants using Riprap and RiboSNitchDB." NAR Genomics and Bioinformatics 2.3 (2020): lqaa057.