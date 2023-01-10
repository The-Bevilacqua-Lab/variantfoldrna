##############################################################################
# Helper functions for running snakemake in tests
# 
# Author: Kobie Kirven
##############################################################################

# -- imports --
import subprocess
import sys

def prCyan(skk):
    print("\033[96m {}\033[00m".format(skk))

def run_snakemake(
    config_args="conda",
    verbose=False,
    snakefile="Snakefile",
    outdir=None,
    extra_args=[],
):
    """
    Run snakemake with the given configfile, and return the exit code.
    """

    # basic command
    cmd = ["snakemake", "-s", snakefile]

    cmd += ["--use-conda", "--conda-frontend", "conda"]

    # add user=specified configfile - try looking for it a few different ways.

    cmd += ["--config"] + config_args

    # snakemake sometimes seems to want a default -j; set it to 1 for now.
    # can overridden later on command line.
    cmd += ["-j", "1"]

    # add rest of snakemake arguments
    cmd += list(extra_args)

    try:
        subprocess.check_call(cmd, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Error in snakemake invocation: {e}", file=sys.stderr)
        return e.returncode

    return 0