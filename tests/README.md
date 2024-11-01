# Testing
This bash script tests each of the different run modes of pipeline at least once to validate things are working as expected.
Before you run the bash script, make changes to the following variables:

- CONDA_ENV_NAME - The name of the conda environment with VariantFoldRNA
- CONDA_ENV_PATH - Path to the directory where the conda environments for the pipeline will be stored
- SINGULARITY_CONTAINER_PATH - Path to the directory where the singularity containers for the pipeline will be stored


## Run the tests
```bash
bash test_all_variantfoldrna_functionality.sh
```