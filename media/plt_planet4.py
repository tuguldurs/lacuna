fieldID = '506c2c3e'
datapath = '../d/'

import numpy  as np
import matplotlib.pyplot as plt
from itertools import product as iterp
from PIL import Image
import cv2 as cv


def getPlanet(fieldID):
    j17 = plt.imread(f'{datapath}planet-jun17/{fieldID}.png')
    j18 = plt.imread(f'{datapath}planet-jun18/{fieldID}.png')
    d17 = plt.imread(f'{datapath}planet-dec17/{fieldID}.png')
    d18 = plt.imread(f'{datapath}planet-dec18/{fieldID}.png')
    return j17, j18, d17, d18

j17, j18, d17, d18 = getPlanet(fieldID)

fig, ax = plt.subplots(ncols=2, nrows=2, tight_layout=True, figsize=(4,4))
ax[0,0].imshow(j17)
ax[0,0].set_title('Jun-2017')
ax[0,1].imshow(d17)
ax[0,1].set_title('Dec-2017')
ax[1,0].imshow(j18)
ax[1,0].set_title('Jun-2018')
ax[1,1].imshow(d18)
ax[1,1].set_title('Dec-2018')
for i,j in iterp(range(2), range(2)):
    ax[i,j].axis('off')
plt.savefig('planet4.png')


def getHighContrast(j17, j18, d17, d18):
    summer = j17 + j18
    summer = summer / np.amax(summer)
    winter = d17 + d18
    winter = winter / np.amax(winter)
    diff = winter * summer
    return diff

imgHC = getHighContrast(j17, j18, d17, d18)
fig, ax = plt.subplots(tight_layout=True, figsize=(4,4))
ax.imshow(imgHC)
ax.axis('off')
plt.savefig('HCimage.png')

img = cv.imread('HCimage.png',0)
clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(4,4))
cl1 = clahe.apply(img)
cv.imwrite('clahe.png', cl1)


img = plt.imread('506c2c3e_mask.png')
plt.imshow(img, cmap=plt.cm.gray)
plt.axis('off')
plt.savefig('mask.png')
