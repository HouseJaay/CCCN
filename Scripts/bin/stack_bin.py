import obspy
import os

datadir = './stack/'
f = open(datadir + 'name_distance', 'r')
dist_bin = 0.1
counts = [0 for _ in range(80)]
st = obspy.Stream()
cur = dist_bin
save = ""

for line in f.readlines():
    temp = line[:-1].split()
    name = temp[0]
    dist = float(temp[1])
    while dist > cur:
        cur += dist_bin
        if save:
            st[0].write(datadir+save, format='SAC')
            save = ""
    idx = int(cur * 10)
    if counts[idx] == 0:
        counts[idx] += 1
        st = obspy.read(datadir + name)
        save = "BIN_%.1f.SAC" % cur
    else:
        counts[idx] += 1
        st[0].data += obspy.read(datadir + name)[0].data
if save:
    st[0].write(datadir+save, format='SAC')

f.close()
