[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: snakefmt](https://img.shields.io/badge/code%20style-snakefmt-000000.svg)](https://github.com/snakemake/snakefmt)

<img src="static/mutafoldrna_logo.png">

MutaFoldRNA is a [Snakemake](https://snakemake.readthedocs.io/en/stable/) pipeline for predicting riboSNitches transcriptome-wide

## Table of Contents
- [Installation](#installation)
- [Quickstart Guide](#quickstart-guide)
  - [Predicting riboSNitches for natural variants](#predicting-ribosnitches-from-natural-variants)
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

### Predicting riboSNitches for natural variants
The three inputs needed to run MutaFoldRNA are a reference genome in FASTA format, a GFF3 file containing transcript annotations, and a VCF file containing the natural variants you want to predict riboSNitches for. An example of those three files for yeast can be found in the `test_data` directory. These files were originally obtaned from ENSEBML and the VCF file was subsetted to just the first 1000 lines. For this example, we will be generating a riboSNitch prediction for each variant in the VCF file. We need to specify which riboSNitch prediction tool we would like to use. Currently, MutaFoldRNA supports SNPfold, RNAsnp, RipRap, and remuRNA. We will use SNPfold for this example. We also need to specify a flanking length for doing the folding of the RNA. Here, we will use a flanking length of 50 nucleotides on each side of the variant. Another important thing we should specify is the path to the singularity environments. Since some of the images are rather large (~1 GB), you want to make sure that you specify a path that has enough space to store the images. Additionally, we are going to specify that we wan to use the canonical and spliced transcripts for our analysis. Also, since we are just interested in generating riboSNitch predictions for the natural variants, we will use the ```--rbsn-only```  flag. While there are many more parameters we can specify, we will just use the defaults for the rest of the parameters. Note that file paths must be absolute. In the following example, the current working directory is stored in the variable ```cwd``` so you do not have to worry about it. This is what the command for our first example would look like:

```bash
cwd=$(pwd)
mutafoldrna \
    --ref-genome ${cwd}/test_data/yeast_ref_genome.fa  \
    --gff ${cwd}/test_data/yeast_gene_model.gff3 \
    --vcf test_data/saccharomyces_cerevisiae_subset.vcf \
    --flank 50 \
    --singularity-path ${cwd}/singularity_envs \
    --singularity-bind ${cwd}/test_data \
    --ribosnitch-tool SNPfold \
    --out-dir yeast_ribosnitches \
    --canonical \
    --spliced \
    --rbsn-only
```

This command will generate a directory called 'yeast_ribosnitches' that contains all of the files needed to run the pipeline. For running the pipeline, simply change into the directory and run the following command:

```bash
bash mutafoldrna.sh
```

Once the pipeline finishes running, you should see a folder titled 'results'. Inside the results directory will be another directory titled 'ribosnitch_predictions'. This folder contains several files, but the most important one is 'combined_ribosnitch_predictions_37.0.txt'. Here, the 37.0 refers to the temperature at which we folded the RNA for the riboSNitch predictions. Here is what the first few lines of the file should look like:

```
Chrom   Pos     Transcript_pos  Ref     Alt     Flank_left      Flank_right     Gene    Match   Type    Strand  Score
I       396     62      C       G       TAACACACACGTGCTTACCCTACCACTTTATACCACCACCACATGCCATA      TCACCCTCACTTGTATACTGATTTTACGTACGCACACGGATGCTACAGTA      YAL069W_mRNA   MATCHED_REF     missense_variant        1       0.867
I       397     63      U       C       AACACACACGTGCTTACCCTACCACTTTATACCACCACCACATGCCATAC      CACCCTCACTTGTATACTGATTTTACGTACGCACACGGATGCTACAGTAT      YAL069W_mRNA   MATCHED_REF     synonymous_variant      1       0.992
```

You can see that there is a lot going here. Each row is a riboSNitch prediction for each variant. The first few columns are the chromosome, position on the chromosome, the position in the transcript, the reference allele, the alternative allele, the sequence 5' of the variant, the sequence 3' of the varaint, the gene name, whether the reference genome matchhed the the reference allele in the VCF file, the class of mutation as identified by VEP, whether the variant was on the positive or negative strand, and the score from the riboSNitch prediction tool we used. This file is tab-seperated and can easily be imported into R or excel for further analysis. 