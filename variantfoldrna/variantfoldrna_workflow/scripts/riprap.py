#!/usr/bin/env python3
"""
This script is the version1.0 of Riprap.
Original Programmer: jianan.lin@jax.org
Version: 1.0
Editing date: Feb 7th, 2020
"""
import os
import os.path
import sys
import re
import time
from subprocess import call
import subprocess
from subprocess import *
import numpy as np
from numpy import *
from scipy.stats import ranksums, ks_2samp
import math
import argparse
from argparse import RawTextHelpFormatter


"""
First, Riprap generated the fasta file using the WT sequence and the SNP information. The fasta file contains the WT and mutant sequences with its ID coming from the input.
"""


def make_fa_file(inputfilename, outputfilepath):
    ifile = open(inputfilename)
    if not os.path.exists(outputfilepath):
        os.makedirs(outputfilepath)
    ofile = open(outputfilepath + "wt_mut_allseq.fa", "w")
    for line in ifile:
        ID, wtseq, SNV = line.strip("\r\n").split("\t")
        Pos = int(SNV[1:-1])
        mutseq = wtseq[: Pos - 1] + SNV[-1] + wtseq[Pos:]
        ofile.write(">" + ID + "_ref\n" + wtseq + "\n>" + ID + "_alt\n" + mutseq + "\n")
    ofile.close()
    ifile.close()
    last_id = ID + "_alt"
    return last_id


"""
We provide the options for user to use one of the following folding algorithms: RNAfold, RNAstructure, and Mfold(UNAfold).

"""

# run RNAfold with a given folder to save the temperary files (output of RNAfold)
def runRNAfold(fafile, dppsfilepath, temp):
    while not os.path.exists(fafile):
        time.sleep(1)
    if os.path.isfile(fafile):
        if not os.path.exists(dppsfilepath):
            os.makedirs(dppsfilepath)
        os.chdir(dppsfilepath)
        commandline1 = (
            "RNAfold -p -T "
            + str(temp)
            + " < "
            + fafile
            + " > "
            + dppsfilepath
            + "rnafold.out"
        )
        process1 = subprocess.Popen(commandline1, stdout=subprocess.PIPE, shell=True)


# transfer format of RNAfold output file to the base pairing probability file
def dpps2ppm(dpps_file):
    ifile = open(dpps_file)
    il, jl, pl = [], [], []
    flag = 0
    while 1:
        line = ifile.readline()
        if line.startswith("showpage"):
            break
        elif line.startswith("/sequence"):
            l1 = ifile.readline().strip()  # read the next line
            seq = l1
            swit = 1  # set sign to 1 for continue reading file
            while swit == 1:
                line = ifile.readline()
                if line.startswith(") } def"):
                    swit = 0  # end sign for stop
                else:
                    seq += line.strip()[:-1]
            seq = seq[:-1]
            seq_len = len(seq)
            # print str(seq) #for debugging
            # print seq_len
        elif line.startswith(("%start", "%data starts")):
            flag = 1
        if flag == 1:
            if line.endswith("ubox\n"):
                tmp = line.strip().split(" ")
                i, j, p = tmp[0], tmp[1], tmp[2]
                il.append(i)
                jl.append(j)
                # print i,j,p
                pl.append(float(p) * float(p))
    ifile.close()
    PPM = np.zeros((seq_len, seq_len))
    for i, item in enumerate(il):
        PPM[int(item) - 1, int(jl[i]) - 1] = pl[i]
    # get lower triangle from the upper triangle
    for i in range(len(seq)):
        for j in range(i, len(seq)):
            PPM[j, i] = PPM[i, j]
            # if PPM[i,j]!=0:
            #    print i,j,PPM[i,j]
    ofilename = dpps_file.strip("_dp.ps") + ".ppm"
    if os.path.isfile(ofilename):
        return 0
    else:
        np.savetxt(ofilename, PPM, delimiter=",")


# Given the RNAfold output folder, perform the transfer function on all the structure files
def alldpps2ppm(dppsfilepath):
    for myfile in os.listdir(dppsfilepath):
        if myfile.endswith("dp.ps"):
            dpps2ppm(myfile)


# As for RNAstructure, first seperate the fasta files to single sequence files and then run RNAstructure in Two steps:a) partition; b) ProbabilityPlot

# convert the pfs.txt files to ppm files
def pfs2ppm(pfsfilename):
    while not os.path.exists(pfsfilename):
        time.sleep(1)
    RS_file = open(pfsfilename)
    seq_len = int(RS_file.readline().strip("\r\n"))
    id_line = RS_file.readline()
    RS_data = RS_file.readlines()
    RS_file.close()
    ## build a zero matrix for the ppm ##
    RS_d = zeros((seq_len, seq_len))
    for line in RS_data:
        tmp = line.strip("\r\n").split()
        i, j, s = int(tmp[0]), int(tmp[1]), float(tmp[2])
        p = math.pow(10, (-s))
        RS_d[i - 1][j - 1] = p
        RS_d[j - 1][i - 1] = p
    ofilename = pfsfilename[:-8] + ".ppm"
    savetxt(ofilename, RS_d, delimiter=",")


# run two steps
def runRNAstructure(fafile, pfsfilepath, temp):
    while not os.path.exists(fafile):
        time.sleep(1)
    if os.path.isfile(fafile):
        if not os.path.exists(pfsfilepath):
            os.makedirs(pfsfilepath)
        ifile = open(fafile)
        while 1:
            line = ifile.readline()
            if len(line) < 1:
                break
            if line.startswith(">"):
                seqname = line.strip()[1:]
                single_fasta = pfsfilepath + seqname + ".fasta"
                ofile = open(single_fasta, "w")
                ofile.write(line)
                seq = ifile.readline()
                ofile.write(seq)
                ofile.close()
                single_pfs = pfsfilepath + seqname + ".pfs"
                cmd = "partition -T {0} {1} {2}".format(
                    str(temp), single_fasta, single_pfs
                )
                Popen(cmd, stdout=PIPE, shell=True).communicate()
                single_txt = single_pfs + ".txt"
                cmd = "ProbabilityPlot {0} {1} -t".format(single_pfs, single_txt)
                while not os.path.exists(single_pfs):
                    time.sleep(1)
                Popen(cmd, stdout=PIPE, shell=True).communicate()
                pfs2ppm(single_txt)
                cmd = "rm {0}".format(single_fasta)
                Popen(cmd, stdout=PIPE, shell=True).communicate()
        ifile.close()


# As for UNAfold, first seperate the fasta files to single sequence files and build a single folder for the UNAfold output,and then run UNAfold PF model
def tmp37plot2ppm(plotfilename, sequence_len):
    while not os.path.exists(plotfilename):
        time.sleep(1)
    una_file = open(plotfilename)
    seq_len = int(sequence_len)
    id_line = una_file.readline()
    una_data = una_file.readlines()
    una_file.close()
    ## build a zero matrix for the ppm ##
    una_d = zeros((seq_len, seq_len))
    for line in una_data:
        tmp = line.strip("\r\n").split()
        i, j, s = int(tmp[0]), int(tmp[1]), float(tmp[2])
        una_d[i - 1][j - 1] = s
        una_d[j - 1][i - 1] = s
    ofilename = plotfilename[:-14] + ".ppm"
    savetxt(ofilename, una_d, delimiter=",")


def runUNAfold(fafile, unafilepath):
    while not os.path.exists(fafile):
        time.sleep(1)
    if os.path.isfile(fafile):
        if not os.path.exists(unafilepath):
            os.makedirs(unafilepath)
        ifile = open(fafile)
        while 1:
            line = ifile.readline()
            if len(line) < 1:
                break
            if line.startswith(">"):
                seqname = line.strip()[1:]
                single_path = unafilepath + seqname + "/"
                if not os.path.exists(single_path):
                    os.makedirs(single_path)
                single_fasta = unafilepath + seqname + "/" + seqname + ".fasta"
                ofile = open(single_fasta, "w")
                ofile.write(line)
                seq = ifile.readline()
                ofile.write(seq)
                ofile.close()
                os.chdir(single_path)
                cmd = "UNAFold.pl --model=PF {0}".format(single_fasta)
                Popen(cmd, stdout=PIPE, shell=True).communicate()
                plotfilename = single_fasta + ".37.plot"
                sequence_len = len(seq.strip())
                tmp37plot2ppm(plotfilename, sequence_len)
                cmd = "mv {0} {1}".format(plotfilename[:-14] + ".ppm", unafilepath)
                Popen(cmd, stdout=PIPE, shell=True).communicate()
                cmd = "rm {0}".format(single_fasta)
                Popen(cmd, stdout=PIPE, shell=True).communicate()
        ifile.close()


def Get_all_prefiles(inputfilename, fafilepath, folding_type, structurefilepath, temp):
    last_id = make_fa_file(inputfilename, fafilepath)
    all_fa = fafilepath + "wt_mut_allseq.fa"
    if folding_type == "RNAfold":
        runRNAfold(all_fa, structurefilepath, temp)
        dppsfile = structurefilepath + last_id + "_dp.ps"
        while not os.path.exists(dppsfile):
            time.sleep(1)
        alldpps2ppm(structurefilepath)
        last_ppm = last_id + ".ppm"
        return last_ppm
    elif folding_type == "RNAstructure":
        runRNAstructure(all_fa, structurefilepath, temp)
    elif folding_type == "UNAfold":
        runUNAfold(all_fa, structurefilepath)


## difference of median BPP (FC) ##
def Getmedian_fc(ppm1, ppm2):
    Seq_len1 = len(ppm1)
    Seq_len2 = len(ppm2)
    averagePP1 = median(ppm1)
    averagePP2 = median(ppm2)
    dis = max(
        (averagePP1 + 0.001) / (float(averagePP2) + 0.001),
        (averagePP2 + 0.001) / (float(averagePP1) + 0.001),
    )
    return dis


## KS test p-value ##
def two_sample_ks_test(xs, ys):
    xsarray = np.array(xs)
    ysarray = np.array(ys)
    t_statistic, p_value = ks_2samp(xsarray, ysarray)
    return p_value


## get median fold change of two bpp vectors ##
def drap(ppm1, ppm2, LB, RB, Pos):
    length_seq = LB + RB + 1
    ppm1seg = ppm1[(Pos - LB - 1) : (Pos + RB)]
    ppm2seg = ppm2[(Pos - LB - 1) : (Pos + RB)]
    dis = Getmedian_fc(ppm1seg, ppm2seg)
    return dis


## find the region with largest score , region is restricted around the SNV ##
def find_region(ppv1, ppv2, Pos, minW):
    minHW = int(int(minW) / 2)
    Rdis = int(len(ppv1) - int(Pos))
    Ldis = int(Pos) - 1
    score = 0
    p_value = 1
    LB_last = int(minHW)
    RB_last = int(minHW)
    score_array = np.zeros((len(ppv1) + 1, len(ppv1) + 1))
    for LB in range(minHW, (Ldis + 1)):
        for RB in range(minHW, (Rdis + 1)):
            p_value_new = two_sample_ks_test(
                ppv1[(int(Pos) - LB - 1) : (int(Pos) + RB)],
                ppv2[(int(Pos) - LB - 1) : (int(Pos) + RB)],
            )
            drap_new = drap(ppv1, ppv2, LB, RB, Pos)
            score_new = drap_new * (-log10(float(p_value_new)))
            # print(score_new,LB,RB)
            score_array[(int(Pos) - LB - 1), (int(Pos) + RB)] = score_new
            if score_new > score:
                score = score_new
                LB_last = LB
                RB_last = RB
                p_value = p_value_new
            else:
                continue
    score = round(score, 3)
    return score, LB_last, RB_last, p_value, score_array


## find the region with largest score , region is freely scanning the entire sequence ##
def find_region_free(ppv1, ppv2, Pos, minW):
    # initiate the window at the beginning of the sequence
    score = 0
    p_value = 1
    LB_last = 0
    RB_last = int(minW)
    # record the score of every scanning region
    score_array = np.zeros((len(ppv1) + 1, len(ppv1) + 1))
    for LB in range(0, (len(ppv1) - minW + 1)):
        for RB in range(LB + minW, len(ppv1) + 1):

            p_value_new = two_sample_ks_test(ppv1[LB:RB], ppv2[LB:RB])
            drap_new = Getmedian_fc(ppv1[LB:RB], ppv2[LB:RB])
            score_new = drap_new * (-log10(float(p_value_new)))
            # print(score_new,LB,RB)
            score_array[LB, RB] = score_new
            if score_new > score:
                score = score_new
                LB_last = LB
                RB_last = RB
                p_value = p_value_new
            else:
                continue
    score = round(score, 3)
    return score, LB_last, RB_last, p_value, score_array


## find the region with largest score , region is fixed by the user ##
def find_region_fix(ppv1, ppv2, LBin, RBin, minW):

    # initiate the window at the beginning of the sequence
    score = 0
    p_value = 1
    LB_last = LBin
    RB_last = LBin + int(minW)
    score_array = np.zeros((len(ppv1) + 1, len(ppv1) + 1))
    for LB in range(LBin, (RBin + 1)):
        for RB in range(LB + minW, RBin + 1):
            p_value_new = two_sample_ks_test(ppv1[LB:RB], ppv2[LB:RB])
            drap_new = Getmedian_fc(ppv1[LB:RB], ppv2[LB:RB])
            score_new = drap_new * (-log10(float(p_value_new)))
            score_array[LB, RB] = score_new
            if score_new > score:
                score = score_new
                LB_last = LB
                RB_last = RB
                p_value = p_value_new
            else:
                continue
    score = round(score, 3)
    return score, LB_last, RB_last, p_value, score_array


def Get_all_score(ppmfilename1, ppmfilename2, Pos, length_seq, minW, fr, LBin, RBin):
    ppm1 = loadtxt(ppmfilename1, delimiter=",", unpack=False)[:length_seq, :length_seq]
    ppm2 = loadtxt(ppmfilename2, delimiter=",", unpack=False)[:length_seq, :length_seq]
    pp1 = ppm1.sum(axis=0)
    pp2 = ppm2.sum(axis=0)
    if fr == 0:
        score, LB, RB, p_value, score_array = find_region(pp1, pp2, Pos, minW)
        windows = int(Pos) - LB
        windowe = int(Pos) + RB
    elif fr == 1:
        score, windows, windowe, p_value, score_array = find_region_free(
            pp1, pp2, Pos, minW
        )
    elif fr == 2:
        score, windows, windowe, p_value, score_array = find_region_fix(
            pp1, pp2, LBin, RBin, minW
        )

    Num = []
    Num.extend([score])
    Num.extend([p_value])
    Num.extend([windows])
    Num.extend([windowe])
    return Num, score_array


## read file and output file ##
def output_score_for_snv(
    input_filename, path_to_ppmfile_folder, outfile_prefix, minW, fr, LBin, RBin, save
):
    ifile = open(input_filename)
    output_filename = outfile_prefix + "_riprap_score.tab"
    ofile = open(output_filename, "w")
    ofile.write("ID,score,p-value,start,end\n")
    for lines in ifile:
        ID, wtseq, SNV = lines.strip("\r\n").split("\t")
        length_seq = len(wtseq)
        Pos = int(SNV[1:-1])
        ppmfilename1 = path_to_ppmfile_folder + ID + "_ref.ppm"
        ppmfilename2 = path_to_ppmfile_folder + ID + "_alt.ppm"
        while not os.path.exists(ppmfilename1):
            time.sleep(1)
        while not os.path.exists(ppmfilename2):
            time.sleep(1)
        if os.path.isfile(ppmfilename1) and os.path.isfile(ppmfilename2):
            myseqfeature, score_array = Get_all_score(
                ppmfilename1, ppmfilename2, Pos, length_seq, minW, fr, LBin, RBin
            )
            ofile.write(ID + "," + str(myseqfeature)[1:-1] + "\n")
            if save == True:
                np.savetxt(outfile_prefix + "_score_matrix.txt", score_array)
    ifile.close()


def Get_all(inputfilename, outfile_prefix, fold_type, minW, fr, LBin, RBin, save, temp):
    inputfilename = os.path.abspath(inputfilename)
    outfile_prefix = os.path.abspath(outfile_prefix)
    raw_dir = os.path.dirname(outfile_prefix)
    fa_path = raw_dir + "/seq/"
    ppm_path = raw_dir + "/ppm/"
    fold_type = int(fold_type)
    if fold_type == 1:  ## RNAfold
        last_ppm = Get_all_prefiles(inputfilename, fa_path, "RNAfold", ppm_path, temp)
        while not os.path.exists(last_ppm):
            time.sleep(1)
        output_score_for_snv(
            inputfilename, ppm_path, outfile_prefix, minW, fr, LBin, RBin, save
        )
    elif fold_type == 2:  ## RNAstructure
        Get_all_prefiles(inputfilename, fa_path, "RNAstructure", ppm_path, temp)
        output_score_for_snv(
            inputfilename, ppm_path, outfile_prefix, minW, fr, LBin, RBin, save
        )
    elif fold_type == 3:  ## UNAfold
        Get_all_prefiles(inputfilename, fa_path, "UNAfold", ppm_path, temp)
        output_score_for_snv(
            inputfilename, ppm_path, outfile_prefix, minW, fr, LBin, RBin, save
        )
    elif fold_type == 0:  ## no folding, existing folder
        output_score_for_snv(
            inputfilename, ppm_path, outfile_prefix, minW, fr, LBin, RBin, save
        )
    if save == False:
        cmd = "rm -r {0}".format(ppm_path)
        Popen(cmd, stdout=PIPE, shell=True).communicate()
        cmd = "rm -r {0}".format(fa_path)
        Popen(cmd, stdout=PIPE, shell=True).communicate()


def garparser():
    argparser = argparse.ArgumentParser(
        description="Riprap: Predicting RNA structural disruptions induced by single nucleotide variants\nVersion: 1.0\n",
        formatter_class=RawTextHelpFormatter,
    )
    argparser.add_argument(
        "-i",
        "--input",
        dest="SNV_file",
        type=str,
        required=True,
        help="Input SNV file with fullpath. Please refer to the webpage for the file format.",
    )
    argparser.add_argument(
        "-o",
        "--outpref",
        dest="out_pref",
        type=str,
        required=True,
        help="Input the prefix of the output file with fullpath to store the output table of Riprap.",
    )
    argparser.add_argument(
        "-t",
        "--foldtype",
        dest="fold_type",
        type=str,
        required=False,
        default="1",
        help="Please provide the folding algorithm you want to use. 1: RNAfold; 2: RNAstructure; 3: Mfold (UNAfold); or 0: No folding.(Used when you have existing files). If not provided, RNAfold will be performed.",
    )
    argparser.add_argument(
        "-w",
        "--minwin",
        dest="minW",
        type=int,
        required=False,
        default=3,
        help="Please provide the minimum spanning window size (nt) to select the structure disrupted region. The default minimum window size is 3nt.",
    )
    argparser.add_argument(
        "-f",
        "--wintype",
        dest="fr",
        type=int,
        required=False,
        default=0,
        help="Please provide the type of spanning window. There are three types of windows available in Riprap: 0: spanning window that include the SNV position; 1: freely spanning window along the entire sequence; 2: spanning window within a fixed region. The first type of window is restricted around the SNV position to select the structure disrupted region, which is the recommended and default option. The second type of window does not have to include the SNV site in searching, which results in longer running time. The last type of window requires the user to provide the start and end site of the interested region on the sequence, which is NOT recommended unless the user know what they are doing. The default is 0, the first type of window.",
    )
    argparser.add_argument(
        "-l",
        "--LBin",
        dest="LBin",
        type=int,
        required=False,
        default=0,
        help="Please provide the index of the left boundary of the pre-selected region. The default is 0, which is the start site of the sequence. Only use this option when you are interested in a specific region with known biology. This option is not recommended.",
    )
    argparser.add_argument(
        "-r",
        "--RBin",
        dest="RBin",
        type=int,
        required=False,
        default=10,
        help="Please provide the index of the right boundary of the pre-selected region. The default is 10, which means the 10th position of the sequence. Only use this option when you are interested in a specific region with known biology. This option is not recommended.",
    )
    argparser.add_argument(
        "-s",
        "--save",
        dest="save",
        type=str,
        required=False,
        default="no",
        help="Whether save the intermediate files. Input yes or no, and default is no.",
    )
    argparser.add_argument(
        "-T",
        "--temperture",
        dest="temp",
        type=float,
        required=False,
        default=37.0,
        help="The temperature for RNA folding. The default is 37.0.",
    )

    return argparser


def RUN():
    argsp = garparser()
    args = argsp.parse_args()
    # If the tool is RNAstructure, make sure we add the data tables to the path:
    if args.fold_type == str(2):
        prefix = os.environ["CONDA_PREFIX"]
        os.environ["DATAPATH"] = "{0}/share/RNAstructure/data_tables/".format(prefix)
    inputfile = args.SNV_file
    output_pre = args.out_pref
    fold_type = args.fold_type
    minW = args.minW
    fr = args.fr
    LBin = args.LBin
    RBin = args.RBin
    save = args.save == "yes"
    temp = args.temp

    start_time = time.time()
    print("Starting...")
    Get_all(inputfile, output_pre, fold_type, minW, fr, LBin, RBin, save, temp)
    print("Finished!")
    print("--- The running time is %s seconds ---" % (time.time() - start_time))


RUN()
