##########################################################################################################
# Scramble the RNA sequence before riboSNitch prediction
##########################################################################################################

#-- Imports -- #
import argparse
import subprocess
import tempfile
from Bio import SeqIO  

if __name__ == "__main__":
    # Add command line arguments
    parser = argparse.ArgumentParser(description="Plot results")
    parser.add_argument("-seq", dest="seq", help="Input RiboSNitch Results File")
    parser.add_argument("-out", dest="out", help="Output folder")
    args = parser.parse_args()

    # Create a temporary file to hold the sequences
    fn = tempfile.NamedTemporaryFile(delete=False)
    fn.close()

    split_line = None
    # Write the sequences to the temporary file
    with open(fn.name, "w") as f:
        for line in open(args.seq).readlines():
            split_line = line.split("\t")
            f.write(f">{'_'.join(split_line[:2])}\n")
            f.write(f"{split_line[4]}{split_line[2]}{split_line[5]}\n")
    
    if split_line:
        # Run the scramble command
        length = str(len(split_line[4])+1)

        # Run the fasta-shuffle-letters command
        subprocess.run(["fasta-shuffle-letters", "-preserve", length, fn.name, str(fn.name) +"_scrambled"]) 

        in_lines = open(args.seq)
        out_file = open(args.out, "w")
        # Write the scrambled sequences to the output file
        for rec in SeqIO.parse(f"{fn.name}_scrambled", "fasta"):
            line = in_lines.readline()
            split_line = line.split("\t")

            # Get the scrambled flanking sequences 
            flank_left = str(rec.seq)[:len(split_line[4])]
            flank_right = str(rec.seq)[len(split_line[4])+1:]
            
            # Write the scrambled sequence to the output file
            split_line[4] = flank_left
            split_line[5] = flank_right
            out_file.write("\t".join(split_line) + "\n")

        # Remove the temporary files
        subprocess.run(["rm", fn.name, f"{fn.name}_scrambled"])

        out_file.close()

    else:
        open(args.out, "w").close()




