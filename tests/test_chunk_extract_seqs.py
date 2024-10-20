import unittest
import subprocess
import os
import tempfile
import shutil

class TestChunkExtractedSequencesScript(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        
        # Create a test input file with sample extracted sequences
        self.input_file = "test_data/chunk_extracted_sequences/extracted_sequences_test.txt"


    def tearDown(self):
        # Remove the temporary directory and all its contents
        shutil.rmtree(self.test_dir)

    def run_chunking_test(self, chunk_total, expected_total_lines):
        # Prepare the command to run the script
        command = ['python3', '../src/variantfoldrna/workflow/scripts/chunk_extracted_seqs.py', 
                   '--input', self.input_file, 
                   '--dir', self.test_dir, 
                   '--chunk-total', str(chunk_total)]
        print(" ".join(command))
        # Execute the script
        subprocess.run(command, check=True)

        # Check the output files
        expected_files = [os.path.join(self.test_dir, 'extracted_seqs_chunks', f'extracted_flank_snp_{i+1}.txt') for i in range(chunk_total)]
        
        total_lines = 0
        for file in expected_files:
            self.assertTrue(os.path.exists(file), f"Expected output file {file} does not exist.")
            with open(file, 'r') as f:
                total_lines += len(f.readlines())
        
        self.assertEqual(total_lines, expected_total_lines, f"Expected total lines: {expected_total_lines}, but got: {total_lines}")

    def test_script_splits_into_2_chunks(self):
        self.run_chunking_test(2, 10)  # Expecting 10 lines total

    def test_script_splits_into_3_chunks(self):
        self.run_chunking_test(3, 10)  # Expecting 10 lines total

    def test_script_splits_into_5_chunks(self):
        self.run_chunking_test(5, 10)  # Expecting 10 lines total

    def test_script_splits_into_1_chunk(self):
        self.run_chunking_test(1, 10)  # Expecting 10 lines total

if __name__ == '__main__':
    unittest.main()