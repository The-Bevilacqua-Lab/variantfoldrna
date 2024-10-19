import unittest
import subprocess
import os
import tempfile
import shutil

class TestSplitFileScript(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        
        # Create a test CSV file
        self.input_file = os.path.join(self.test_dir, 'test_input.csv')
        with open(self.input_file, 'w') as f:
            f.write("Line 1\nLine 2\nFLANK Line 3\nLine 4\nLine 5\n")

    def tearDown(self):
        # Remove the temporary directory and all its contents
        shutil.rmtree(self.test_dir)

    def run_chunking_test(self, chunk_total, expected_total_lines):
        # Prepare the command to run the script
        command = ['python3', '../src/variantfoldrna/workflow/scripts/chunk_csv.py', 
                   '--input', self.input_file, 
                   '--dir', self.test_dir, 
                   '--chunk-total', str(chunk_total)]
        
        # Execute the script
        subprocess.run(command, check=True)

        # Check the output files
        expected_files = [os.path.join(self.test_dir, 'csv_chunks', f'csv_chunk_{i+1}.csv') for i in range(chunk_total)]
        
        total_lines = 0
        for file in expected_files:
            self.assertTrue(os.path.exists(file), f"Expected output file {file} does not exist.")
            with open(file, 'r') as f:
                total_lines += len(f.readlines())
        
        self.assertEqual(total_lines, expected_total_lines, f"Expected total lines: {expected_total_lines}, but got: {total_lines}")

    def test_script_splits_into_2_chunks(self):
        self.run_chunking_test(2, 4)  # Expecting 4 lines total (excluding "FLANK" line)

    def test_script_splits_into_3_chunks(self):
        self.run_chunking_test(3, 4)  # Expecting 4 lines total

    def test_script_splits_into_5_chunks(self):
        self.run_chunking_test(4, 4)  # Expecting 4 lines total

    def test_script_splits_into_1_chunk(self):
        self.run_chunking_test(1, 4)  # Expecting 4 lines total

    def test_script_exits_if_chunks_exceed_lines(self):
        # Prepare the command to run the script with too many chunks
        command = ['python3', '../src/variantfoldrna/workflow/scripts/chunk_csv.py', 
                   '--input', self.input_file, 
                   '--dir', self.test_dir, 
                   '--chunk-total', '10']

        # Execute the script and check for a system exit
        with self.assertRaises(subprocess.CalledProcessError):
            subprocess.run(command, check=True)

if __name__ == '__main__':
    unittest.main()