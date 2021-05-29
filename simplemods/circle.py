"""
create circular masks where areas are set by the given Plotsie
and centered at given displacement
"""

datapath = '../../../d/'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

def getPlanet(fieldID):
    j17 = plt.imread(f'{datapath}planet-jun17/{fieldID}.png')
    j18 = plt.imread(f'{datapath}planet-jun18/{fieldID}.png')
    d17 = plt.imread(f'{datapath}planet-dec17/{fieldID}.png')
    d18 = plt.imread(f'{datapath}planet-dec18/{fieldID}.png')
    return j17, j18, d17, d18


def getHighContrast(j17, j18, d17, d18):
    summer = j17 + j18
    summer = summer / np.amax(summer)
    winter = d17 + d18
    winter = winter / np.amax(winter)
    diff = winter * summer
    return diff

def getXY(fieldID, sampleShape):
    cX = 10.986328125 / 2
    cY = 10.985731758 / 2
    train = pd.read_csv(f'{datapath}train-unique.csv')
    row = train.loc[train['ID'] == f'id_{fieldID}']
    x0, y0 = sampleShape[1]//2, sampleShape[0]//2
    x1 = x0 - np.round(row.x.values[0] / cX * sampleShape[1])
    y1 = y0 + np.round(row.y.values[0] / cY * sampleShape[0])
    # radius based on Plot_size
    m2  = row.PlotSize_acres.values[0] * 4047.
    r   = (m2 / np.pi)**0.5
    rpx = r / 4.7
    return [x0, y0, x1, y1, rpx]

def makeMasks():
    train = pd.read_csv(f'{datapath}train-unique.csv')
    for i in range(300):

        # create high contrast composite
        fieldID = train.ID[i].split('_')[-1]
        j17, j18, d17, d18 = getPlanet(fieldID)
        imgHC = getHighContrast(j17, j18, d17, d18)
        imgHC = (imgHC * 255).astype(np.uint8)
        img = Image.fromarray(imgHC)
        img.save(f'hc{i:04}.png')

        # create mask
        gray = np.dot(imgHC[... , :3] , [0.299 , 0.587, 0.114])
        mask = np.zeros(gray.shape)
        xy = getXY(fieldID, gray.shape)
        for k,j in np.ndindex(gray.shape):
            x     = k - xy[2]
            y     = j - xy[3]
            r2dot = (x*x + y*y) ** 0.5
            if r2dot < xy[-1]: mask[j, k] = 1
        mask = (mask).astype(np.uint8)
        img = Image.fromarray(mask)
        img.save(f'hc{i:04}_mask.png')

        print(f' done {i}')



if __name__ == '__main__':
    makeMasks()
