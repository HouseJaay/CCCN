#!/usr/bin/env python

import sys
import getopt
import os
from os.path import join
import numpy as np
import obspy
from CCCN.cccn.make_one_folder import transf, transf_hinet, perwhiten, docc, inm_stack
from glob import glob
import logging


def Usage():
    print("preparation.py -f<f1/f2/f3/f4> -d<dt> -c<cut1/cut2> -l<maxlag> [-n<node>]")
    print("    [-C<channel_list>] [-t<seed|hinet>] [-w<half-length>] [-S<suffix>] floder_lst")
    print("-c Cut raw waveforms from \"cut1\" to \"cut2\"")
    print("-d Specify sample rate after downsample")
    print("-f Specify frequence window when whitening")
    print("-l Specify lag of cross-correlation function")
    print("-n The number of thread at computing cross-correlation. (1 default)")
    print("-t Format of sacfile name (\"seed\" or \"hinet\")\n"
          "     \"seed\": 2016.001.00.00.00.0195.IC.BJT.00.BHZ.M.SAC, SAC_PZs_IC_BJT_BHZ_00\n"
          "     \"hinet\": N.KKCH.U.SAC, N.KKCH.U.SAC_PZ")
    print("-w Half-length of time window at normlization")
    print("-C Specify Channels. channels should be complete like 'BHZ' for seed format"
          "multiple channels should be separated by /, like '-CBHZ/BHE'")
    print("-S Specify suffix of sacfiles")
    print("-D delete temporary files")
    print("-K path of stack files, if specified, stack CCF immediately and delete correlation files")


global fft_all
argv = sys.argv[1:]
if os.path.isfile(argv[-1]):
    folder_lst = argv[-1]
else:
    print("folder list not exist")
    sys.exit(1)

try:
    opts, args = getopt.getopt(argv, "w:f:S:d:c:l:t:C:n:K:D")
except getopt.GetoptError:
    print('Arguments are not found!')
    sys.exit(1)
if not opts:
    Usage()
    sys.exit(1)

suffix = "SAC"
wlen = 0
istransf = False
isdelete = False
ch = ['Z']
node = 1
dformat = "seed"
isstack = False
for op, value in opts:
    if op == "-w":
        wlen = float(value)
    elif op == "-f":
        f1 = float(value.split('/')[0])
        f2 = float(value.split('/')[1])
        f3 = float(value.split('/')[2])
        f4 = float(value.split('/')[3])
    elif op == "-S":
        suffix = value
    elif op == "-d":
        dt = float(value)
    elif op == "-c":
        cuttime1 = float(value.split('/')[0])
        cuttime2 = float(value.split('/')[1])
    elif op == "-l":
        lag = float(value)
    elif op == "-t":
        istransf = True
        if value in ["seed", "hinet"]:
            dformat = value
        else:
            print("wrong option in \"-t\" argument")
            sys.exit(1)
    elif op == "-C":
        ch = value.split('/')
    elif op == "-n":
        node = int(value)
    elif op == "-D":
        isdelete = True
    elif op == "-K":
        isstack = True
        stack_path = value
    else:
        Usage()
        sys.exit(1)

logging.basicConfig(filename=folder_lst+'.log', level=logging.INFO)
with open(folder_lst) as flst:
    for folder in flst.readlines():
        folder = folder.strip()
        print(folder)
        folder_name = folder.split()[0]
        reftime = obspy.UTCDateTime(folder.split()[1])
        nt = int(np.floor((cuttime2 - cuttime1)/dt))
        if istransf:
            print("\t1st transfering instromental reponse...")
            if dformat == "seed":
                transf(folder_name, suffix, dt, ch=ch)
            elif dformat == "hinet":
                transf_hinet(folder_name, suffix, dt, ch=ch)
            else:
                print("wrong option in \"-F\" argument...")
                sys.exit(1)
        print("\t2nd perwhiten...")
        ev_num = perwhiten(folder_name, dt, wlen, cuttime1, cuttime2, reftime, f1, f2, f3, f4, ch=ch)
        # if ev_num <= 1:
        #    print("not enough event in folder %s" % folder_name)
        #    continue
        print("\t3th compute cross-correlation...")
        sta_pair = docc(folder_name, nt, dt, lag, reftime, f2, f3, node)
        if isdelete:
            print("\tremove temporary files")
            for cname in ch:
                files = glob(join(folder_name, "TRANS_*.%s" % cname))
                for file_name in files:
                    os.remove(file_name)
        if isstack:
            print("\tstack CCFs")
            inm_stack(join(stack_path, "stack_%s" % folder_lst))
