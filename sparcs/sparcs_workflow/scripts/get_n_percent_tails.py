#######################################################################
# Get the top n_percent of riboSNitches from the riboSNitch predictions
#
#
# Author: Kobie Kirven
#######################################################################

# ----- Import modules ----#
import argparse
import pandas as pd 

# ----- Functions ------#
def get_top_n_percent(riboSNitch_predictions, top_n_percent):
    """
    Get the top n_percent of riboSNitches from the riboSNitch predictions
    """
    # Read in the riboSNitch predictions
    riboSNitch_predictions_df = pd.read_csv(riboSNitch_predictions, sep="\t")

    # Sort the dataframe by the score column
    riboSNitch_predictions_df = riboSNitch_predictions_df.sort_values(by=['Score'])

    # Get the number of rows in the dataframe
    num_rows = riboSNitch_predictions_df.shape[0]

    # Get the number of rows to keep
    num_rows_to_keep = int(num_rows * top_n_percent)

    # Get the top n_percent of riboSNitches
    top_n_percent_riboSNitches = riboSNitch_predictions_df.head(num_rows_to_keep)

    # Return the top n_percent of riboSNitches
    return top_n_percent_riboSNitches

def get_bottom_n_percent(riboSNitch_predictions, top_n_percent):
    """
    Get the bottom n_percent of riboSNitches from the riboSNitch predictions
    """
    # Read in the riboSNitch predictions
    riboSNitch_predictions_df = pd.read_csv(riboSNitch_predictions, sep="\t")

    # Sort the dataframe by the score column
    riboSNitch_predictions_df = riboSNitch_predictions_df.sort_values(by=['Score'])

    # Get the number of rows in the dataframe
    num_rows = riboSNitch_predictions_df.shape[0]

    # Get the number of rows to keep
    num_rows_to_keep = int(num_rows * top_n_percent)

    # Get the bottom n_percent of riboSNitches
    bottom_n_percent_riboSNitches = riboSNitch_predictions_df.tail(num_rows_to_keep)

    # Return the bottom n_percent of riboSNitches
    return bottom_n_percent_riboSNitches

# ----- Main ------#
if __name__ == "__main__":

    # Parse the command-line arguments
    parser = argparse.ArgumentParser(
        description="Get the top n_percent of riboSNitches from the riboSNitch predictions"
    )
    parser.add_argument(
        "--input",
        dest="riboSNitch_predictions",
        help="Path to the riboSNitch predictions file",
        required=True,
    )
    parser.add_argument(
        "--top-output",
        dest="top_output",
        help="Path to the output file",
        required=True,
    )

    parser.add_argument(
        "--bottom-output",
        dest="bottom_output",
        help="Path to the output file",
        required=True,
    )

    parser.add_argument(
        "--n-percent",
        dest="top_n_percent",
        help="Top n percent of riboSNitches to keep",
        required=True,
    )

    args = parser.parse_args()

    # Get the top n_percent of riboSNitches
    top_n_percent_riboSNitches = get_top_n_percent(args.riboSNitch_predictions, float(args.top_n_percent))

    # Write the top n_percent of riboSNitches to a file
    top_n_percent_riboSNitches.to_csv(args.top_output, sep="\t", index=False)

    # Get the bottom n_percent of riboSNitches
    bottom_n_percent_riboSNitches = get_bottom_n_percent(args.riboSNitch_predictions, float(args.top_n_percent))

    # Write the bottom n_percent of riboSNitches to a file
    bottom_n_percent_riboSNitches.to_csv(args.bottom_output, sep="\t", index=False)
