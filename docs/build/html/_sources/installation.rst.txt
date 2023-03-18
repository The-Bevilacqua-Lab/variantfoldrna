=============
Installation
=============

Prerequisites:
--------------
:mod:`SPARCS` only requires that your system has Snakemake and the `conda <https://docs.conda.io/en/latest/>`_ package manager installed.
All other dependencies are handled by Snakemake directly. You can check that both are installed by running::
    
    conda -h
    snakemake -h

Information on how to install Snakemake can be found `here <https://snakemake.readthedocs.io/en/stable/getting_started/installation.html>`_.

Installing the pipeline:
----------------------------
To download the pipeline, simply navigate to the directory of your choice and run::

    git clone https://github.com/The-Bevilacqua-Lab/SPARCS.git
    pip3 install SPARCS/

And that's it! You should not have SPARCS installed. To test that the installation was successful, run::

    sparcs --help

