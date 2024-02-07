[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: snakefmt](https://img.shields.io/badge/code%20style-snakefmt-000000.svg)](https://github.com/snakemake/snakefmt)

<img src="static/variantfoldrna_logo.png">

VariantFoldRNA is a [Snakemake](https://snakemake.readthedocs.io/en/stable/) pipeline for predicting SNPs that alter RNA structure (riboSNitches) transcriptome-wide.

## Table of Contents
- [Installation](#installation)
- [Quickstart Guide](#quickstart-guide)
  - [Predicting riboSNitches for natural variants](#predicting-ribosnitches-from-natural-variants)
  - [Predicting riboSNitches for synthetic variants](#predicting-ribosnitches-from-synthetic-variants)
  - [Predicting riboSNitches at different temperatures](#predicting-ribosnitches-at-different-temperatures)
- [Command Line Options](#command-line-options)
- [Trouble Shooting](#trouble-shooting)

## Installation 
There are only two dependencies for VariantFoldRNA: [Snakemake](https://snakemake.readthedocs.io/en/stable/) and [singularity](https://sylabs.io/guides/3.7/user-guide/quick_start.html#quick-installation-steps). 

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


<details>
<summary>Issues with singularity</summary>
<br>
If you encounter an issue with the singularity images where you do not have enough space to build them, you can download the images using the following command:

```bash
wget -o ${cwd}/singularity_envs.tar.gz https://sourceforge.net/projects/mutafoldrna-containers/files/latest/download -P ${cwd}
```

Then, you can extract the images using the following command:

```bash
tar -xzf ${cwd}/singularity_envs.tar.gz -C ${cwd}
```
</details>

### Predicting riboSNitches for synthetic variants
If you are interested in sudying the other possible variants at positions where you observe natural variants, you can do that easily with MutaFoldRNA. The command is going to look very similar to the one used in the previous example, except this time we will substitute the ```--rbsn-only``` flag for the ```--null-only``` flag. This will generate riboSNitch predictions for all possible variants at positions where we observed natural variants. Here is what the command would look like:

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
    --null-only
```

Like before, you should see a `results` directory. Inside the results directory will be another directory titled `ribosnitch_predictions_null`. This folder contans a file titled `combined_ribosnitch_predictions_37.0.txt`. This file is formatted the same as the previous file, except it contains riboSNitch predictions for all possible variants at positions where we observed natural variants.

### Predicting riboSNitches at different temperatures
The MutaFoldRNA pipeline has functionality for generating riboSNitch predictions over a range of temperatures. This could be useful for studying riboSNitches that are temperature sensitive. To do this, we need to specify a minimum temperature, a maximum temperature, and a temperature step. The minimum and maximum temperatures should be seperated by an '@' symbol. The temperature step is the amount to increase the temperature by at each step. Here is an example of what the command would look like:  

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
    --rbsn-only \
    --temperature 10@40 \
    --temp-step 5
```
The results folder will contain a subfolder called `ribosnitch_predictions`. Inside of the `ribosnitch_predictions` contains mutiple files, one for each temperature. The file names are formatted as `combined_ribosnitch_predictions_<temperature>.txt`.

## Command Line Options
```
usage: mutafoldrna [-h] --vcf VCF --gff GFF --ref-genome FASTA [--out-dir OUT] [--spliced] [--canonical] [--chunks CHUNKS] [--cores CORES]
                   [--null-model-total NULL_MODEL_TOTAL] [--structure-pred-tool STRUCTURE_PRED_TOOL] [--ribosnitch-tool RIBOSNITCH_TOOL]
                   [--flank RIBOSNITCH_FLANK] [--singularity-bind SINGULARITY_BIND] [--temperature TEMPERATURE] [--temp-step TEMP_STEP]
                   [--minwindow MINWINDOW] [--singularity-path SINGULARITY] [--force] [--cluster] [--cluster-info CLUSTER_INFO] [--jobs JOBS] [--null-only]
                   [--rbsn-only] [--top-n-percent TOP_N_PERCENT] [--shuffle-null]

Run the mutafoldrna pipeline

optional arguments:
  -h, --help            show this help message and exit
  --vcf VCF             Absolute ath to VCF file (If not specified, will check the current directory
  --gff GFF             Absolute path to GFF file (If not specified, will check the current directory
  --ref-genome FASTA    Absolute path to the reference genome file (If not specified, will check the current directory
  --out-dir OUT         Path to output directory (If not specified, will create a new directory named 'mutafoldrna_output' in the current directory
  --spliced             Used the spliced form of transcripts
  --canonical           Used only the canonical transcripts
  --chunks CHUNKS       Number of chunks to split the VCF file into (Default: 10)
  --cores CORES         Number of cores to use (Default: 1)
  --structure-pred-tool STRUCTURE_PRED_TOOL
                        Structure prediction tool to use (RNAfold or RNAstructure, Default: RNAfold)
  --ribosnitch-tool RIBOSNITCH_TOOL
                        RiboSNitch prediction tool to use (SNPfold or Riprap, Default: SNPfold)
  --flank RIBOSNITCH_FLANK
                        Flanking length for RiboSNitch prediction (Default: 40)
  --singularity-bind SINGULARITY_BIND
                        Path to directory to bind to singularity
  --temperature TEMPERATURE
                        Temperature for structural prediction (Default: 37.0)
  --temp-step TEMP_STEP
                        Temperature step for structural prediction (Default: 5)
  --minwindow MINWINDOW
                        Minimum window size for Riprap (Default: 3)
  --singularity-path SINGULARITY
                        Path to directory that holds the singularity containers
  --force               Create the output directory even if it already exists
  --cluster             flag to indicate that the pipeline will be run on a cluster
  --cluster-info CLUSTER_INFO
                        Info for jobs to be submitted to the cluster.
  --jobs JOBS           Number of jobs to be submitted to the cluster.
  --null-only           Only the riboSNitch predictions for building the null distribution.
  --rbsn-only           Only the riboSNitch predictions, no null distribution.
  --top-n-percent TOP_N_PERCENT
                        The top n percent to define as riboSNitches (default = 0.05)
  ```

## Trouble Shooting
If you encounter any issues with MutaFoldRNA, please open an issue on the github page. 

### FAQ:
- **Q:** I am getting an error with the normalize rule where it says one of the ID lines is too long and it is not a valid VCF file. What is going on?
  - **A:** For some reason, bcftools does not like the ID columns for some VCF files. To fix this, you can use the `remove_id.py` script located in the `test_data` folder. This script will replace the ID column with a '.'. 