#############################################################
# A wrapper to run R2EasyR on the 
#
############################################################

# -- Imports -- #
import argparse 
import os 
import tempfile
import pandas as pd


def remove_text_from_svg(svg_path, output_path):
    """
    Remove unwanted text lines from the SGV file
    """

    # Read in the SVG file
    lines = open(svg_path).readlines()

    # Create a list to hold the modified SVG
    out_lines = []

    # Loop through the lines in the SVG
    for i in range(len(lines)):

        # Skip the lines that contain text
        if 'text' in lines[i] or 'tspan' in lines[i]:
            continue
        else:
            out_lines.append(lines[i])
            if 'path' in lines[i]:
                out_lines += lines[i+1:]
                break

    # Write the modified SVG to the output file
    with open(output_path, 'w') as f:
        f.writelines(out_lines)

def create_r2easyr_input(sequence, bppm, secondary, output_path):
    """
    Creates a file with the input for R2EasyR
    """
    # Create a temporary file to write the input to
    temp_file = tempfile.NamedTemporaryFile(delete=False)

    # Create a dataframe to hold the input
    df = pd.DataFrame(columns=['N',"Nucleotide","Dotbracket","Reactivity"])

    # Split the input into lists
    reactivity = [x for x in bppm.split(",")]
    seq = [x for x in sequence]
    n = [x for x in range(1,len(sequence)+1)]
    dotbracket = [x for x in secondary]

    # Add the lists to the dataframe
    df['N'] = n
    df['Nucleotide'] = seq
    df['Dotbracket'] = dotbracket
    df['Reactivity'] = reactivity

    # Write the dataframe to the temporary file
    df.to_csv(temp_file.name, index=False)

    # Return the path to the temporary file
    return temp_file.name


if __name__ == "__main__":

    # Create an argument parser
    parser = argparse.ArgumentParser(description='A simple Python script with command-line arguments')
    parser.add_argument('--in', dest='input', help='input file')
    parser.add_argument('--out-dir', dest='out_dir', help='output directory')
    
    # Parse the command-line arguments
    args = parser.parse_args()

    # Get the path to the script
    path = os.path.dirname(os.path.realpath(__file__))

    # Check to see if the output directory exists
    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)

    # Read in the input file as a pandas dataframe
    df = pd.read_csv(args.in_file, sep="\t", header=0)

    # Loop though the dataframe
    for i in range(len(df)):
        sequence = df.iloc[i]['Ref_Sequence']
        bppm = df.iloc[i]['Ref_BPPM']
        secondary = df.iloc[i]['Ref_Secondary']

        # Create the input file for R2EasyR
        input_file = create_r2easyr_input(sequence, bppm, secondary, f"{args.out_dir}/{i}.csv")

        # Run the scipt
        os.system(f"Rscript {path}/r2easyr.R {args.input} seq_{i}_ref")

        # Run R2R
        os.system(f"r2r --disable-usage-warning seq_{i}_ref.r2r_meta seq_{i}_temp_ref.svg")

        # Remove text from the SVG and save the modified SVG
        remove_text_from_svg(f"seq_{i}_temp_ref.svg", f"{args.out_dir}/seq_{i}_ref.svg")
        os.rm(f"seq_{i}_temp_ref.svg")

        #Do the same for the alt sequence
        sequence = df.iloc[i]['Alt_Sequence']
        bppm = df.iloc[i]['Alt_BPPM']
        secondary = df.iloc[i]['Alt_Secondary']

        # Create the input file for R2EasyR
        input_file = create_r2easyr_input(sequence, bppm, secondary, f"{args.out_dir}/{i}.csv")

        # Run the scipt
        os.system(f"Rscript {path}/r2easyr.R {args.input} seq_{i}_alt")

        # Run R2R
        os.system(f"r2r --disable-usage-warning seq_{i}_alt.r2r_meta seq_{i}_temp_alt.svg")

        # Remove text from the SVG and save the modified SVG
        remove_text_from_svg(f"seq_{i}_temp_alt.svg", f"{args.out_dir}/seq_{i}_alt.svg")
        os.rm(f"seq_{i}_temp_alt.svg")
        
