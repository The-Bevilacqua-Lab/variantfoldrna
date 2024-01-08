############################################################
# Creates an PDF to hold the top n riboSNitch candidates
#
# Author: Kobie Kirven
############################################################

# -- Imports -- #
import argparse
import pandas as pd
import os

if __name__ == "__main__":

    # Create an argument parser
    parser = argparse.ArgumentParser(description='A simple Python script with command-line arguments')
    parser.add_argument('--in', dest='input', help='input file')
    parser.add_argument('--svg-dir', dest='svg_dir', help='directory containing SVG files')
    parser.add_argument('--out', dest='output', help='output file')
    
    # Parse the command-line arguments
    args = parser.parse_args()

    # Read in the input file as a pandas dataframe
    df = pd.read_csv(args.in_file, sep="\t", header=0)

    # Create an html file with rows for each candidate where the columns 
    # Are the chromosome, chromosome position, transcript position, ref, alt, score, reference structure, and the alternative structure
    with open(args.output, 'w') as f:

        # Write the header to the html file
        f.write("<html><head><style><style>table{width:100%;border-collapse:collapse;margin-bottom:20px;font-family:Arial,sans-serif;font-size:14px}th,td{padding:10px;text-align:left;border:1px solid #ddd}th{background-color:#f5f5f5;font-weight:bold;color:#333}tr:nth-child(even){background-color:#f9f9f9}tbody tr:hover{background-color:#eaf6ff}</style><table><thead><tr><th>Column 1</th><th>Column 2</th><th>Column 3</th></tr></thead><tbody><tr><td>Data 1</td><td>Data 2</td><td>Data 3</td></tr><tr><td>Data 4</td><td>Data 5</td><td>Data 6</td></tr><!-- Add more rows as needed --></tbody></table></style></head><body><table><tr><th>Chrom</th><th>Pos</th><th>Transcript_pos</th><th>Ref</th><th>Alt</th><th>Score</th><th>Ref_Structure</th><th>Alt_Structure</th></tr>\n")

        
        # Loop through the dataframe and write the rows to the html file
        for index, row in df.iterrows():
                
                # Get the path to the SVG files
                ref_svg_path = os.path.join(f"{args.svg_dir}", f"seq_{index}_ref.svg")
                alt_svg_path = os.path.join(f"{args.svg_dir}", f"seq_{index}_alt.svg")
    
                # Write the row to the html file
                f.write(f"<tr><td>{str(row['Chrom'])}</td><td>{str(row['Pos'])}</td><td>{str(row['Transcript_pos'])}</td><td>{str(row['Ref'])}</td><td>{str(row['Alt'])}</td><td>{str(row['Score'])}</td><td><img src='{ref_svg_path}'></td><td><img src='{alt_svg_path}'></td></tr>\n")

    # Create a PDF from the html file
    os.system(f"wkhtmltopdf {args.output} {args.output.replace('.html', '.pdf')}")

    # Remove the html file
    os.system(f"rm {args.output}")
    


