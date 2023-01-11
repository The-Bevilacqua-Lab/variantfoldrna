##############################################################################
# This script will test all of the rules in the extract_seqs.smk file
#
# Author: Kobie Kirven
# Assmann and Bevilacqua Labs
# The Pennsylvania State University
##############################################################################

# Imports
import os
import unittest
from utils import run_snakemake, prCyan
import gffutils as gff
import pandas as pd 

# Get the path to the workflow on the current computer 
workflow_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
workflow_path = "/".join(workflow_path.split("/"))

# Names of the test GTF files
GTFs = ["Arabidopsis_thaliana.TAIR10.55.gtf", "Candida_auris.GCA002759435v2.55.gtf",
        "Drosophila_melanogaster.BDGP6.32.55.gtf", "Escherichia_coli_w_gca_000184185.ASM18418v1.55.gtf",
        "lncRNA.gtf"]

links = ["https://ftp.ensemblgenomes.org/pub/plants/release-55/gtf/arabidopsis_thaliana/Arabidopsis_thaliana.TAIR10.55.gtf.gz",
"https://ftp.ensemblgenomes.org/pub/release-55/fungi/gtf/candida_auris/Candida_auris.GCA002759435v2.55.gtf.gz",
"https://ftp.ensemblgenomes.org/pub/release-55/metazoa/gtf/drosophila_melanogaster/Drosophila_melanogaster.BDGP6.32.55.gtf.gz",
"https://ftp.ensemblgenomes.org/pub/bacteria/release-55/gtf/bacteria_26_collection/escherichia_coli_w_gca_000184185/Escherichia_coli_w_gca_000184185.ASM18418v1.55.gtf.gz",
"http://3dgenome.hzau.edu.cn/RiceLncPedia/media/lnc/lncRNA.gtf"]
    
        
# Make sure that the output folder does not already exist.
# If it does, delete it.
if os.path.exists(f"{workflow_path}/tests/.test_output/extract_seqs_test"):
    os.system(f"rm -rf {workflow_path}/tests/.test_output/extract_seqs_test")

class TestPipeline(unittest.TestCase):

    def test_build_gffutils(self):
        """
        Test to make sure that the gffutils database is built properly
        """
        # Let the user know what is happening
        prCyan("Currently testing: build_gffutils")

        for i in range(len(GTFs)):
            
            # Download the GTF file if it does not already exist
            if not os.path.exists(f"{workflow_path}/tests/test_data/gtfs/{GTFs[i]}"):
                os.system(f"wget {links[i]} --no-check-certificate -P {workflow_path}/tests/test_data/gtfs/ > /dev/null 2>&1")
            
            if GTFs[i] != "lncRNA.gtf":
                os.system(f"gunzip {workflow_path}/tests/test_data/gtfs/{GTFs[i]}.gz")

            # Targets
            targets = [f"create_gffutils"]

            # Change the config file parameters
            working_dir = f"{workflow_path}/tests/.test_output"
            out_name = "extract_seqs_test"
            gtf = f"{workflow_path}/tests/test_data/gtfs/{GTFs[i]}"

            # Run the Snakemake pipeline
            run_snakemake(snakefile=f"{workflow_path}/workflow/Snakefile", config_args=[f"working_directory={working_dir}", f"out_name={out_name}", f"gtf_file={gtf}"], extra_args=targets)

            # Check to make sure the file exists
            self.assertTrue(os.path.exists(f"{workflow_path}/tests/.test_output/extract_seqs_test/temp/{GTFs[i][:-4]}.db"))

            # Check to make sure that the file is a gffutils database
            db = gff.FeatureDB(f"{workflow_path}/tests/.test_output/extract_seqs_test/temp/{GTFs[i][:-4]}.db")

            # Remove the file
            os.system(f"rm {workflow_path}/tests/.test_output/extract_seqs_test/temp/{GTFs[i][:-4]}.db")

            # Remove the GTF file
            os.system(f"rm {workflow_path}/tests/test_data/gtfs/{GTFs[i]}")

        # Remove the output folder
        os.system(f"rm -rf {workflow_path}/tests/.test_output/extract_seqs_test")

    def test_remove_duplicates(self):
        """
        Test that the script properly removes variants that occur more than once 
        in the file
        """
        # Create the output folder if it does not already exists
        if not os.path.exists(f"{workflow_path}/tests/.test_output/extract_seqs_test/temp"):
            os.makedirs(f"{workflow_path}/tests/.test_output/extract_seqs_test/temp")

        # Copy the test file to the folder
        os.system(f"cp {workflow_path}/tests/test_data/extract_sequences/test_duplicates.txt {workflow_path}/tests/.test_output/extract_seqs_test/temp/extracted_flank_snp.txt")

        # Targets
        targets = [f"{workflow_path}/tests/.test_output/extract_seqs_test/temp/extracted_flank_snp_no_duplicates.txt"]

        # Change the config file parameters
        working_dir = f"{workflow_path}/tests/.test_output"
        out_name = "extract_seqs_test"

        # Run the Snakemake pipeline
        run_snakemake(snakefile=f"{workflow_path}/workflow/Snakefile", config_args=[f"working_directory={working_dir}", f"out_name={out_name}"], extra_args=targets)

        # Check to make sure there are only 11 variants in the output file 
        with open(f"{workflow_path}/tests/.test_output/extract_seqs_test/temp/extracted_flank_snp_no_duplicates.txt") as fn:
            lines = fn.readlines()
            self.assertEqual(len(lines),11)

    def test_extract_sequences(self):
        """
        Make sure that the sequences are propperly extracted from the genome
        """
        # Download chromosome 1 of the mouse genome
        if not os.path.exists(f"{workflow_path}/tests/test_data/get_read_data/mouse.fa"):
            os.system(f"wget https://ftp.ensembl.org/pub/release-108/fasta/mus_musculus/dna/Mus_musculus.GRCm39.dna.chromosome.1.fa.gz -P {workflow_path}/tests/test_data/get_read_data/")
            os.system(f"gunzip {workflow_path}/tests/test_data/get_read_data/Mus_musculus.GRCm39.dna.chromosome.1.fa.gz")
            os.system(f"mv {workflow_path}/tests/test_data/get_read_data/Mus_musculus.GRCm39.dna.chromosome.1.fa {workflow_path}/tests/test_data/get_read_data/mouse.fa")

        # Download the mouse GTF file
        if not os.path.exists(f"{workflow_path}/tests/test_data/get_read_data/mouse.gtf"):
            os.system(f"wget https://ftp.ensembl.org/pub/release-108/gtf/mus_musculus/Mus_musculus.GRCm39.108.gtf.gz -P {workflow_path}/tests/test_data/get_read_data/")
            os.system(f"gunzip {workflow_path}/tests/test_data/get_read_data/Mus_musculus.GRCm39.108.gtf.gz")
            os.system(f"mv {workflow_path}/tests/test_data/get_read_data/Mus_musculus.GRCm39.108.gtf {workflow_path}/tests/test_data/get_read_data/mouse.gtf")

        # Create the output folder if it does not already exists
        if not os.path.exists(f"{workflow_path}/tests/.test_output/extract_seqs_test/temp/extracted_sequences/"):
            os.makedirs(f"{workflow_path}/tests/.test_output/extract_seqs_test/temp/extracted_sequences")

        if not os.path.exists(f"{workflow_path}/tests/.test_output/extract_seqs_test/temp/annotated_vcf_chunks_effects/"):
            os.makedirs(f"{workflow_path}/tests/.test_output/extract_seqs_test/temp/annotated_vcf_chunks_effects")
        
        # Copy the test file to the folder
        os.system(f"cp {workflow_path}/tests/test_data/get_read_data/test_coords.txt {workflow_path}/tests/.test_output/extract_seqs_test/temp/annotated_vcf_chunks_effects/vcf_no_header_1_annotated_one_per_line.txt")

        # Targets
        targets = [f"{workflow_path}/tests/.test_output/extract_seqs_test/temp/extracted_sequences/extracted_seqs_1.txt"]

        # Change the config file parameters
        working_dir = f"{workflow_path}/tests/.test_output"
        out_name = "extract_seqs_test"
        gtf = f"{workflow_path}/tests/test_data/get_read_data/mouse.gtf"
        genome = f"{workflow_path}/tests/test_data/get_read_data/mouse.fa"

        # Run the Snakemake pipeline
        run_snakemake(snakefile=f"{workflow_path}/workflow/Snakefile", config_args=[f"working_directory={working_dir}", f"out_name={out_name}", f"gtf_file={gtf}", f"ref_genome={genome}", "chunks=1", "flank_len=10"], extra_args=targets)

        # Check to make sure the file exists
        self.assertTrue(os.path.exists(f"{workflow_path}/tests/.test_output/extract_seqs_test/temp/extracted_sequences/extracted_seqs_1.txt"))

        # Check to make sure that the correct SNPs were found. We will only check the first 5 columns
        snps = pd.read_csv(f"{workflow_path}/tests/.test_output/extract_seqs_test/temp/extracted_sequences/extracted_seqs_1.txt", sep="\t", header=None)
        snps = snps.iloc[:,[0,1,2,3,4]]
        
        # Change the column names to match the output of the script
        snps.columns = ["chrom", "pos", "ref", "alt", "read_data"]

        # Read in the correct output
        true_snps = pd.read_csv(f"{workflow_path}/tests/test_data/get_read_data/correct_output.txt", sep="\t", header=None)
        true_snps = true_snps.iloc[:,[0,1,2,3,5]]

        # Change the column names to match the output of the script
        true_snps.columns = ["chrom", "pos", "ref", "alt", "read_data"]

        # Check to make sure that the correct SNPs were found
        self.assertEqual(snps.equals(true_snps), True)

    def test_combine_extracted_sequences(self):
        """
        Make sure that the extracted sequence chunks are combined correctly
        """
        # Create the path to the input data if it does not already exist 
        if not os.path.exists(f"{workflow_path}/tests/.test_output/extract_seqs_test/temp/annotated_vcf_chunks_effects/"):
            os.makedirs(f"{workflow_path}/tests/.test_output/extract_seqs_test/temp/annotated_vcf_chunks_effects")

        # Copy the test file to the foler 5 times
        for i in range(1,6):
            os.system(f"cp {workflow_path}/tests/test_data/get_read_data/correct_output.txt {workflow_path}/tests/.test_output/extract_seqs_test/temp/annotated_vcf_chunks_effects/vcf_no_header_{i}_annotated_one_per_line.txt")

        # Targets
        targets = ["combine_extracted_sequences"]

        # Change the config file parameters
        working_dir = f"{workflow_path}/tests/.test_output"
        out_name = "extract_seqs_test"
        chunks = 5

        # Run the Snakemake pipeline
        run_snakemake(snakefile=f"{workflow_path}/workflow/Snakefile", config_args=[f"working_directory={working_dir}", f"out_name={out_name}", "chunks=5"], extra_args=targets)

        # Check to make sure the file exists and that it contains 55 lines
        self.assertTrue(os.path.exists(f"{workflow_path}/tests/.test_output/extract_seqs_test/temp/extracted_sequences/extracted_seqs.txt"))
        self.assertEqual(len(open(f"{workflow_path}/tests/.test_output/extract_seqs_test/temp/extracted_sequences/extracted_seqs.txt").readlines()), 55)
        
if __name__ == '__main__':
    unittest.main()