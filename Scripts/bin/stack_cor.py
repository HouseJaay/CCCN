import obspy
from glob import glob
import os
import pandas as pd
import numpy as np


ch = '2'
datadir = '/share/home/goxu/hao_shijie/sichuan/ZlandDEC/'
freq = '0.2to16.0_COR/'


stack_dir = '/scratch/goxu/hao_shijie/mongolia/data_conti/stack/'
data_dir = '/scratch/goxu/hao_shijie/mongolia/data_conti/stack/stack_*.lst/'
for d in glob(data_dir):
    print(d)
    for fpath in glob(d + 'COR_*.SAC'):
        sac = os.path.basename(fpath)
        st0 = obspy.read(fpath)
        if any(np.isnan(st0[0].data)):
            print("nan!! %s" % fpath)
            continue
        st0[0].data = st0[0].data / np.max(st0[0].data)
        if os.path.exists(stack_dir + sac):
            st1 = obspy.read(stack_dir + sac)
            st1[0].data += st0[0].data
            st1[0].write(stack_dir + sac)
        else:
            st0[0].write(stack_dir + sac)
