#!/bin/bash

#################################################################
# This script tests all the functionality of the variantfoldrna
# to make sure that the program is working as expected.
#################################################################

# Name of the conda environment that contains the variantfoldrna pipeline
CONDA_ENV_NAME="varfold_test"

# Path to the conda environments
CONDA_ENV_PATH="/storage/home/kjk6173/scratch/conda_envs"

# Path to the singularity containers
SINGULARITY_CONTAINER_PATH="/storage/home/kjk6173/scratch/singularity_envs"

# Get the current directory
CURRENT_DIR=$(pwd)

eval "$(conda shell.bash hook)"
conda activate varfold_test
echo $CONDA_ENV_NAME

# Function to check for errors
check_error() {
    if [ $? -ne 0 ]; then
        echo "Error: The previous command failed."
        exit 1
    fi
}

# Test the variantfoldrna pipeline

# 1. Test variantfoldrna pipeline with the default parameters
echo "Testing variantfoldrna pipeline with the default parameters..."
variantfoldrna run --ref-genome=${CURRENT_DIR}/test_data/pipeline_input/yeast_ref_genome.fa --vcf=${CURRENT_DIR}/test_data/pipeline_input/saccharomyces_cerevisiae_subset.vcf --gff=${CURRENT_DIR}/test_data/pipeline_input/yeast_gene_model.gff3 --use-singularity --singularity-prefix=${SINGULARITY_CONTAINER_PATH} --conda-prefix=${CONDA_ENV_PATH} -F
check_error

# 2. Test variantfoldrna pipeline with the --canonical flag
echo "Testing variantfoldrna pipeline with the --canonical flag..."
variantfoldrna run --ref-genome=${CURRENT_DIR}/test_data/pipeline_input/yeast_ref_genome.fa --vcf=${CURRENT_DIR}/test_data/pipeline_input/saccharomyces_cerevisiae_subset.vcf --gff=${CURRENT_DIR}/test_data/pipeline_input/yeast_gene_model.gff3 --canonical --use-singularity --singularity-prefix=${SINGULARITY_CONTAINER_PATH} --conda-prefix=${CONDA_ENV_PATH} -F
check_error

# 3. Test variantfoldrna pipeline with the --spliced flag
echo "Testing variantfoldrna pipeline with the --spliced flag..."
variantfoldrna run --ref-genome=${CURRENT_DIR}/test_data/pipeline_input/yeast_ref_genome.fa --vcf=${CURRENT_DIR}/test_data/pipeline_input/saccharomyces_cerevisiae_subset.vcf --gff=${CURRENT_DIR}/test_data/pipeline_input/yeast_gene_model.gff3 --spliced --use-singularity --singularity-prefix=${SINGULARITY_CONTAINER_PATH} --conda-prefix=${CONDA_ENV_PATH} -F
check_error

# 4. Test variantfoldrna pipeline with both the --canonical and --spliced flags
echo "Testing variantfoldrna pipeline with both the --canonical and --spliced flags..."
variantfoldrna run --ref-genome=${CURRENT_DIR}/test_data/pipeline_input/yeast_ref_genome.fa --vcf=${CURRENT_DIR}/test_data/pipeline_input/saccharomyces_cerevisiae_subset.vcf --gff=${CURRENT_DIR}/test_data/pipeline_input/yeast_gene_model.gff3 --canonical --spliced --use-singularity --singularity-prefix=${SINGULARITY_CONTAINER_PATH} --conda-prefix=${CONDA_ENV_PATH} -F
check_error

# 5. Test variantfoldrna pipeline with the --flank-len flag
echo "Testing variantfoldrna pipeline with the --flank-len flag..."
variantfoldrna run --ref-genome=${CURRENT_DIR}/test_data/pipeline_input/yeast_ref_genome.fa --vcf=${CURRENT_DIR}/test_data/pipeline_input/saccharomyces_cerevisiae_subset.vcf --gff=${CURRENT_DIR}/test_data/pipeline_input/yeast_gene_model.gff3 --flank-len=60 --use-singularity --singularity-prefix=${SINGULARITY_CONTAINER_PATH} --conda-prefix=${CONDA_ENV_PATH} -F
check_error

# 6. Test variantfoldrna pipeline with the --chunks flag
echo "Testing variantfoldrna pipeline with the --chunks flag..."
variantfoldrna run --ref-genome=${CURRENT_DIR}/test_data/pipeline_input/yeast_ref_genome.fa --vcf=${CURRENT_DIR}/test_data/pipeline_input/saccharomyces_cerevisiae_subset.vcf --gff=${CURRENT_DIR}/test_data/pipeline_input/yeast_gene_model.gff3 --chunks=3 --use-singularity --singularity-prefix=${SINGULARITY_CONTAINER_PATH} --conda-prefix=${CONDA_ENV_PATH} -F
check_error

# 7. Test variantfoldrna pipeline using all 4 ribosnitch prediction tools
echo "Testing variantfoldrna pipeline using all 4 ribosnitch prediction tools..."
variantfoldrna run --ref-genome=${CURRENT_DIR}/test_data/pipeline_input/yeast_ref_genome.fa --vcf=${CURRENT_DIR}/test_data/pipeline_input/saccharomyces_cerevisiae_subset.vcf --gff=${CURRENT_DIR}/test_data/pipeline_input/yeast_gene_model.gff3 --ribosnitch-prediction-tool=SNPfold,RipRap,remuRNA,RNAsnp:p-value --use-singularity --singularity-prefix=${SINGULARITY_CONTAINER_PATH} --conda-prefix=${CONDA_ENV_PATH} -F
check_error

# 8. Test variantfoldrna pipeline with the --temp-step and --temperature flags
echo "Testing variantfoldrna pipeline with the --temp-step and --temperature flags..."
variantfoldrna run --ref-genome=${CURRENT_DIR}/test_data/pipeline_input/yeast_ref_genome.fa --vcf=${CURRENT_DIR}/test_data/pipeline_input/saccharomyces_cerevisiae_subset.vcf --gff=${CURRENT_DIR}/test_data/pipeline_input/yeast_gene_model.gff3 --temp-step=5 --temperature=-35@40 --use-singularity --singularity-prefix=${SINGULARITY_CONTAINER_PATH} --conda-prefix=${CONDA_ENV_PATH} -F
check_error

# Check to make sure that all of the final output files have the same number of lines
# This is a simple check to make sure that the pipeline ran successfully
for file in ${CURRENT_DIR}/variantfoldrna_output/ribosnitch_predictions/* ; do
    num_lines=$(wc -l < "$file")
    if [ $num_lines -ne 0 ]; then
        echo "$file: $num_lines lines"
    else
        echo "Error: File $file is empty"
        exit 1
    fi
done

# 9. Test variantfoldrna pipeline on just synonymous SNPs
echo "Testing variantfoldrna pipeline on just synonymous SNPs..."
variantfoldrna run --ref-genome=${CURRENT_DIR}/test_data/pipeline_input/yeast_ref_genome.fa --vcf=${CURRENT_DIR}/test_data/pipeline_input/saccharomyces_cerevisiae_subset.vcf --gff=${CURRENT_DIR}/test_data/pipeline_input/yeast_gene_model.gff3 --use-singularity --singularity-prefix=${SINGULARITY_CONTAINER_PATH} --conda-prefix=${CONDA_ENV_PATH} --variant-annotation-type='synonymous_variant' -F
check_error

# 10. Test variantfoldrna pipeline on just synonymous SNPs with the --canonical and --spliced flags
echo "Testing variantfoldrna pipeline on just synonymous SNPs with the --canonical and --spliced flags..."
variantfoldrna run --ref-genome=${CURRENT_DIR}/test_data/pipeline_input/yeast_ref_genome.fa --vcf=${CURRENT_DIR}/test_data/pipeline_input/saccharomyces_cerevisiae_subset.vcf --gff=${CURRENT_DIR}/test_data/pipeline_input/yeast_gene_model.gff3 --canonical --spliced --use-singularity --singularity-prefix=${SINGULARITY_CONTAINER_PATH} --conda-prefix=${CONDA_ENV_PATH} --variant-annotation-type='synonymous_variant' -F
check_error

# 11. Test variantfoldrna pipeline with the --output-dir flag
echo "Testing variantfoldrna pipeline with the --output-dir flag..."
variantfoldrna run --ref-genome=${CURRENT_DIR}/test_data/pipeline_input/yeast_ref_genome.fa --vcf=${CURRENT_DIR}/test_data/pipeline_input/saccharomyces_cerevisiae_subset.vcf --gff=${CURRENT_DIR}/test_data/pipeline_input/yeast_gene_model.gff3 --out-dir=${CURRENT_DIR}/pipeline_output --use-singularity --singularity-prefix=${SINGULARITY_CONTAINER_PATH} --conda-prefix=${CONDA_ENV_PATH} -F
check_error

# 12. Test variantfoldrna pipeline with using the csv input option
echo "Testing variantfoldrna pipeline with using the csv input option..."
variantfoldrna run --csv=${CURRENT_DIR}/test_data/pipeline_input/test_csv.csv --use-singularity --singularity-prefix=${SINGULARITY_CONTAINER_PATH} --conda-prefix=${CONDA_ENV_PATH} -F
check_error

# 13. Test variantfoldrna pipeline with using the csv input option and only conda
echo "Testing variantfoldrna pipeline with using the csv input option..."
variantfoldrna run --csv=${CURRENT_DIR}/test_data/pipeline_input/test_csv.csv --conda-prefix=${CONDA_ENV_PATH}1 -F
check_error

# 14. Test variantfoldrna pipeline with CSV input and different temperature ranges
echo "Testing variantfoldrna pipeline with CSV input and different temperature ranges..."
variantfoldrna run --csv=${CURRENT_DIR}/test_data/pipeline_input/test_csv.csv --temp-step=5 --temperature=-35@40 --use-singularity --singularity-prefix=${SINGULARITY_CONTAINER_PATH} --conda-prefix=${CONDA_ENV_PATH} -F
check_error

# 15. Test variantfoldrna pipeline with CSV input and all ribosnitch prediction tools
echo "Testing variantfoldrna pipeline with CSV input and all ribosnitch prediction tools..."
variantfoldrna run --csv=${CURRENT_DIR}/test_data/pipeline_input/test_csv.csv --ribosnitch-prediction-tool=SNPfold,RipRap,remuRNA,RNAsnp:p-value --use-singularity --singularity-prefix=${SINGULARITY_CONTAINER_PATH} --conda-prefix=${CONDA_ENV_PATH} -F
check_error

echo "All tests completed successfully."
