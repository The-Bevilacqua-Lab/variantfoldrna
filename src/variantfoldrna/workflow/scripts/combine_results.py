###############################################################
# Combine the multiple files for riboSNitch prediction
###############################################################

# Imports 
import sys
import argparse

def count_lines(file_path):
    """
    count the number of lines in a file
    """
    with open(file_path, 'r') as file:
        return sum(1 for _ in file)

def combine_files(file_list, output_file, line_count):
    """
    Combine the specified files by taking the first column 
    from the first file and the last column from the remaining files.
    """

    # Open all input files
    files = [open(file, 'r') for file in file_list]
    
    # Open the output file
    with open(output_file, 'w') as out:
        for i in range(line_count):
            # Read all lines from the first file and write them to the output file
            first_file_lines = files[0].readline()

            # Extract the last column from each of the remaining files
            last_columns = [file.readline().strip().split('\t')[-1] for file in files[1:]]
            # Write the last columns to the output file
            out.write(first_file_lines.strip() + "\t" + '\t'.join(last_columns) + '\n')

    # Close all input files
    for file in files:
        file.close()

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Combine TSV files.")
    parser.add_argument('input_files', nargs='+', help='List of input TSV files')
    parser.add_argument('output_file', help='Output TSV file')

    args = parser.parse_args()
    # Example usage
    args.input_files.sort(reverse=True)
    line_count = count_lines(args.input_files[0])
    # Combine the specified files
    combine_files(args.input_files, args.output_file, line_count)
