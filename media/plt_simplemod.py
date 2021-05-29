datapath = '../d/'

import numpy  as np
import pandas as pd
import matplotlib.pyplot as plt

from itertools import product as iterp
from skimage.transform import warp_polar
from skimage.io import imread as rdtif


train = pd.read_csv(f'{datapath}train-unique.csv')
etrain = pd.read_csv(f'{datapath}extra_train.csv')
trainall = pd.concat([train, etrain], ignore_index=True)


psz = trainall.PlotSize_acres

x, y = trainall.x, trainall.y
d = np.sqrt(x*x + y*y)

fs = 13

fig, ax = plt.subplots(tight_layout=True)
ax.hist(d, density=True, color='steelblue', alpha=0.5, bins=30)
ax.set_xlabel('distance [km]', fontsize=fs)
ax.set_ylabel('PDF', fontsize=fs)
ax.set_xlim(-0.02,1.98)
plt.savefig('dist_hist.png')

adeg = np.rad2deg(np.arctan2(y, x))
arad = np.arctan2(y, x)

plt.figure()
plt.scatter(adeg+180, d, c=psz, s=psz*50, cmap='tab10', alpha=0.75)
plt.xlabel('angle [deg]', fontsize=fs)
plt.ylabel('distance [km]', fontsize=fs)
plt.ylim(0,1.79)
plt.xlim(0, 360)
cb = plt.colorbar()
cb.set_label(label='Area [acres]', fontsize=fs)
plt.tight_layout()
plt.savefig('bubbles.png')

fig = plt.figure()
ax  = fig.add_subplot(projection='polar')
c   = ax.scatter(arad, d, c=psz, s=psz*20, cmap='tab10', alpha=0.75)
plt.tight_layout()
plt.savefig('polar.png')
