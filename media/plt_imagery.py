import matplotlib.pyplot as plt
import numpy as np

def getBands(fname):
    bW, bT = [], []
    with open(fname, 'r') as f:
        lines = f.readlines()
        for line in lines:
            entries = line.strip().split()
            bW.append(float(entries[1]))
            bT.append(entries[2])
    return bW, bT

def getYSent(bandW):
    return [bandW for i in range(12)]

def getYPlan(bandW):
    return [bandW for i in range(4)]

fname = 'bands.dat'
bW, bT = getBands(fname)
PbW = [496.6, 560, 664.5]

xSent = np.arange(12) / 12. + 2015
xPlan = np.arange(4)  * 0.5 + 2017.5
colS, colP = 'tomato', 'steelblue'
sS,   sP   = 40, 80
xmin, xmax = 2014.6, 2019.1
ymin, ymax = 400, 2250
fs         = 17

fig, ax = plt.subplots(tight_layout=True, figsize=(10,5))

for W in bW:
    ySent = getYSent(W)
    ax.scatter(xSent, ySent, c=colS, s=sS)

for W in PbW:
    yPlan = getYPlan(W)
    ax.scatter(xPlan, yPlan, c=colP, s=sP)

for i in range(len(bT)):
    if i not in [4,5,7]: ax.text(xmin, bW[i], bT[i], rotation=30)

ax.set(xlim=[xmin, xmax], ylim=(ymin, ymax))
ax.set_ylabel('Band Wavelength [nm]', fontsize=fs)
ax.set_xlabel('Year', fontsize=fs)
ax.set_xticklabels(['', 2015, '', 2016, '', 2017, '', 2018, '', 2019])

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

#ax.scatter([0,0], [0,0], c=colS, s=sS, label='Sentinel-2')
#ax.scatter([0,0], [0,0], c=colP, s=sP, label='Planet')
#plt.legend(loc='lower center', frameon=True, facecolor='lightgray', fontsize=fs)

plt.savefig('imagery.png')
