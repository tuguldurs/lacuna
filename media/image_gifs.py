import os
import matplotlib.pyplot as plt
import numpy as np
from skimage.io import imread as rdtif
from itertools import product as iterp

def getSentinelTimeData(path2tif, filterCloudy=True):
    """
    process input Sentinel TIFF file to map its contents into a dictionary
    with filter keys and monthly images as values

    note: it won't process images with number of channels other than 192

    when filterCloudy flag is True:
    - excludes cloudy images based on cloud-mask (filter#16)
    - final dictionary contains 13 real filter data
    """

    # filter and month IDs
    filters = np.arange(16, dtype=int) + 1
    months  = np.arange(12) + 1

    # read TIFF file into 3D array
    img = rdtif(path2tif)

    # stop if its a funky image, proceed only if there are usual 192 channels:
    if img.shape[-1] != 192: exit(f' cannot process this funky image with {img.shape[-1]} channels')

    # initialize the dict with empty list for each filter
    d = {}
    for f in filters: d[f] = []

    # populate with 2D images
    for i, j in iterp(months, filters):

        channel = (i - 1) * len(filters) + j - 1

        # append normalized image
        maxFrame = np.amax(img[:, :, channel])
        if maxFrame == 0.:
            d[j].append(img[:, :, channel])
        else:
            d[j].append(img[:, :, channel] / maxFrame)

    # exclude cloudy images
    if filterCloudy:

        for f in filters:
            for month in months:

                # max value of cloud mask image
                maxCloudMask = np.amax(d[16][month-1])

                # its cloudy if max is not 0
                if maxCloudMask != 0: d[f][month-1] = None

        # we don't need the last 3 elements
        del d[16] # cloudmask itself
        del d[15] # QA20
        del d[14] # QA10

    return d

def getPlanet(fieldID):
    j17 = plt.imread(f'{datapath}planet-jun17/{fieldID}.png')
    j18 = plt.imread(f'{datapath}planet-jun18/{fieldID}.png')
    d17 = plt.imread(f'{datapath}planet-dec17/{fieldID}.png')
    d18 = plt.imread(f'{datapath}planet-dec18/{fieldID}.png')
    return [j17, d17, j18, d18]

fieldID = '66cfc4c2'
datapath = '../d/'
dS = getSentinelTimeData(f'{datapath}sentinel/{fieldID}.tif')

for i in range(0,12):
    m = i + 1
    fig, ax = plt.subplots(tight_layout=True, figsize=(4,4))
    ax.imshow(dS[4][i], cmap=plt.cm.gray)
    ax.set(title=f'field: {fieldID}  month: {m:02d}')
    savename = f'sentinel{i:03}.png'
    plt.savefig(savename)

os.system('convert -delay 20 -loop 0 sentinel*.png sentinel.gif')

imgs = getPlanet(fieldID)
dt = ['jun17', 'dec17', 'jun18', 'dec18']
i = 0
for img in imgs:
    fig, ax = plt.subplots(tight_layout=True, figsize=(6,6))
    ax.imshow(img)
    ax.set(title=f'field: {fieldID}  date: {dt[i]}')
    savename = f'planet{i:03}.png'
    plt.savefig(savename)
    i += 1

os.system('convert -delay 40 -loop 0 planet*.png planet.gif')
