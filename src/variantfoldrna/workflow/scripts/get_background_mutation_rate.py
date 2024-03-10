####################################################################
# Get the background mutation rate based on the intergenic SNPs
#
####################################################################

# Import modules
import argparse

def get_comp(seq):
    """
    Get the reverse complement of the sequence 
    """
    conversion_dict = {"A":"U","C":"G","G":"C","U":"A"}
    return "".join([conversion_dict[x] for x in seq])[::-1]

def get_mutation_keys()
    # Create a dictionary to hold the tri-nucleotides and the 
    mut_key = {}

    nucs = ["A","C","G","U"]
    mut_key = {}

    for x in nucs:
        for y in nucs:
            for z in nucs:
                mut_key[f"{x}{y}{z}"] = {}
                for nuc in nucs:
                    if nuc != y:
                        mut_key[f"{x}{y}{z}"][nuc] = 0
    return mut_key

def get_background_mutation_rate(snp_file):
    """
    Get the background mutation rate based on the intergenic SNPs
    """
    mut_key = get_mutation_keys()
    file = open(snp_file, "r")
    for row in tqdm(file):
        row = row.split("\t")
        flank_left = row[5][-1].replace("T","U")
        flank_right = row[6][0].replace("T","U")
        
        ref = row[3].replace('T','U')
        alt = row[4].replace('T','U')

        try:
            if row[10].strip("\n") == 'positive':
                mut_key[f"{flank_left}{ref}{flank_right}"][alt] += 1

            elif row[10].strip("\n") == 'negative':
                mut_key[f"{flank_right}{get_comp(ref)}{flank_left}"][get_comp(alt)] += 1
        except:
            pass
    file.close()

    return mut_key

def main():
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='Get the background mutation rate based on the intergenic SNPs')
    parser.add_argument('snp_file', type=str, help='The file containing the SNPs')
    args = parser.parse_args()

    # Get the background mutation rate
    mut_key = get_background_mutation_rate(args.snp_file)

    # Write the mutation rate dict to a json file
    with open("background_mutation_rate.json", "w") as file:
        json.dump(mut_key, file)
    
if __name__ == "__main__":
    main()