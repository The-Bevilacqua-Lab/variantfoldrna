[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: snakefmt](https://img.shields.io/badge/code%20style-snakefmt-000000.svg)](https://github.com/snakemake/snakefmt)

<img src="static/mutafoldrna_logo.png">

MutaFoldRNA is a [Snakemake](https://snakemake.readthedocs.io/en/stable/) pipeline for predicting riboSNitches transcriptome-wide

## Table of Contents
- [Installation](#installation)
- [Quickstart Guide](#quickstart-guide)
  - [Predicting riboSNitches from natural variants](#predicting-ribosnitches-from-natural-variants)
## Installation 
There are only two dependenceis for MutaFoldRNA: [Snakemake](https://snakemake.readthedocs.io/en/stable/) and [singularity](https://sylabs.io/guides/3.7/user-guide/quick_start.html#quick-installation-steps). 

Once you have snakemake and singularity installed, he easiest way to install MutaFoldRNA is via pip:

```bash
pip install mutafoldrna
```
You can also install MutaFoldRNA from source:

```bash
git clone https://github.com/The-Bevilacqua-Lab/mutafoldrna.git
cd mutafoldrna
pip install .
```

## Quickstart Guide
MutaFoldRNA is built using the Snakemake workflow management system. The good new is that you do not need to know anything about Snakemake to run MutaFoldRNA. The pipeline is designed to be a  command-line tool that generates all of the necessary files needed to run the pipeline. This quickstart guide is meant to help you get the pipeline up and running as quickly as possible for whatever task you are trying to accomplish.

### Predicting riboSNitches from natural variants
The three inputs needed to run MutaFoldRNA are a reference genome in FASTA format, a GTF file containing transcript annotations, and a VCF file containing the natural variants you want to predict riboSNitches for.