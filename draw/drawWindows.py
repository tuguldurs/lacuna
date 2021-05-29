"""
variant of draw.py made to work on Windows-Anaconda3
changes made by: Michael Darcy

usage: same as draw.py
"""


datapath = 'C:/Users/micha/OneDrive/Documents/GitHub/Lacuna/'

import numpy as np
import pandas as pd
import pygame as pg
import pygame.gfxdraw
import sys,os,math
import matplotlib.pyplot as plt
from multiprocessing import Process
from PIL import Image, ImageDraw
from itertools import product as iterp

startpoint = None
endpoint = None
start =  None


def rgb2gray(rbgimg):
    """
    convert RGB to grayscale
    """
    gray = lambda rgb : np.dot(rgb[... , :3] , [0.299 , 0.587, 0.114])
    grayimg = gray(rbgimg)

    return grayimg / np.amax(grayimg)


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


def getEnhancedBW(diff):
    diff = rgb2gray(diff)
    diff[diff > 0.35] = 0.35
    return diff / np.amax(diff)


def makeHighres(imgHC):
    # make sure there are no black pixels
    for i,j in np.ndindex(imgHC.shape[0],imgHC.shape[1]):
        if sum(imgHC[i,j]) == 0:
            imgHC[i,j,0] = 0.01
            imgHC[i,j,1] = 0.01
            imgHC[i,j,2] = 0.01

    imgHC = (imgHC * 255).astype(np.uint8)
    img = Image.fromarray(imgHC)
    #
    img = img.resize((800, 800))
    draw = ImageDraw.Draw(img)
    draw.ellipse(((392,392),(408,408)), fill='blue')
    img.save('highres.png')


def getXY(fieldID, sampleShape):
    cX = 10.986328125 / 2
    cY = 10.985731758 / 2
    train = pd.read_csv(f'{datapath}train-unique.csv')
    row = train.loc[train['ID'] == f'id_{fieldID}']
    x0, y0 = sampleShape[1]//2, sampleShape[0]//2
    x1 = x0 - np.round(row.x.values[0] / cX * sampleShape[1])
    y1 = y0 + np.round(row.y.values[0] / cY * sampleShape[0])
    # radius based on Plot_size
    m2  = row.PlotSize_acres.values[0] * 4047
    r   = (m2 / np.pi)**0.5
    rpx = r / 4.7
    return [x0, y0, x1, y1, rpx]


def finalImage(fieldID):
    """

    """
    sampleimg = Image.open(f'{datapath}planet-jun17/{fieldID}.png')
    original = sampleimg.size
    img = Image.open('tmp.png')
    savename = f'{fieldID}.png'
    img.resize(original).save(savename)



def launchGuidePlot(args):
    j17, j18, d17, d18 = args[0], args[1], args[2], args[3]
    imgHC, BW = args[4], args[5]
    xy = args[6]
    fig, ax = plt.subplots(nrows=3, ncols=2, figsize=(8,12), sharex=True, sharey=True)
    ax[0,0].imshow(imgHC)
    ax[0,0].set_title('Summer x Winter')
    ax[0,1].imshow(BW, cmap=plt.cm.gray)
    ax[0,1].set_title('Enhanced Gscale')
    ax[1,0].imshow(j17)
    ax[1,0].set_title('June 2017')
    ax[1,1].imshow(d17)
    ax[1,1].set_title('December 2017')
    ax[2,0].imshow(j18)
    ax[2,0].set_title('June 2018')
    ax[2,1].imshow(d18)
    ax[2,1].set_title('December 2018')
    for i,j in iterp(range(3),range(2)):
        ax[i,j].plot([xy[0],xy[2]], [xy[1],xy[3]], c='yellow', linewidth=1)
        ax[i,j].scatter(xy[0], xy[1], marker='o', c='blue')
        ax[i,j].scatter(xy[2], xy[3], marker='*', c='red')
        areacircle = plt.Circle((xy[2],xy[3]), xy[-1], color='red', alpha=0.2)
        if i == 0 and j == 0: ax[i,j].add_patch(areacircle)
    plt.tight_layout()
    plt.show()

def main():
    j17, j18, d17, d18 = getPlanet(sys.argv[1])
    xy    = getXY(sys.argv[1], j17.shape)
    imgHC = getHighContrast(j17, j18, d17, d18)
    BW    = getEnhancedBW(imgHC)
    makeHighres(imgHC)
    p = Process(target=launchGuidePlot, args=([j17, j18, d17, d18, imgHC, BW, xy],))
    p.start()


    ################################################################################
    #################################### DRAW ######################################
    ################################################################################

    pg.init()
    pg.event.set_allowed([pg.QUIT,pg.MOUSEMOTION,pg.MOUSEBUTTONDOWN,pg.KEYDOWN])

    bg = pygame.image.load('highres.png')

    # Settings:
    fps = 120
    font = pg.font.SysFont('consolas',20)
    screenres = (800,800)
    realres = (screenres[0]*1.2,screenres[1]*1.2)

    updated = False
    dirtyrects = []

    # Colors | R | G | B | A |
    clear =  (  0,  0,  0,  0)
    black =  (  0,  0,  0)

    # Surfaces:
    window = pg.display.set_mode(screenres,pg.DOUBLEBUF)
    canvas = pg.Surface((realres[0],realres[1]*1.0)).convert_alpha()
    latest1 = canvas.copy()
    latest2 = canvas.copy()
    latest3 = canvas.copy()
    latest4 = canvas.copy()
    latest5 = canvas.copy()
    layers = [latest1,latest2,latest3,latest4,latest5]
    for layer in layers:
        layer.fill(clear)
    overlay = pg.Surface(screenres).convert_alpha()

    # Rects:
    realrect = pg.Rect(0,0,realres[0],int(realres[1]*1))
    screenrect = pg.Rect(0,0,screenres[0],int(screenres[1]*1))

    r = 5
    clr = black
    startpoint = None
    print (startpoint)
    endpoint = None
    ongoing = False
    undone = 0
    maxundone = 0
    holdingclick = False

    def drawline():
        global startpoint, endpoint, start
        if startpoint == None:
            startpoint = x,y
        endpoint = x,y
        if r > 1:
            if startpoint != endpoint:
                dx,dy = endpoint[0]-startpoint[0],endpoint[1]-startpoint[1]
                angle = math.atan2(-dy,dx)%(2*math.pi)
                dx,dy = math.sin(angle)*(r*0.999),math.cos(angle)*(r*0.999)
                a = startpoint[0]+dx,startpoint[1]+dy
                b = startpoint[0]-dx,startpoint[1]-dy
                c = endpoint[0]-dx,endpoint[1]-dy
                d = endpoint[0]+dx,endpoint[1]+dy
                pointlist = [a,b,c,d]
                pg.draw.polygon(latest1,clr,pointlist)
            pg.draw.circle(latest1,clr,(x,y),r)
        else:
            pg.draw.line(latest1,clr,startpoint,endpoint,r)
        startpoint = x,y

    def shiftdown():
        for layer in reversed(layers):
            if layer == latest5:
                canvas.blit(latest5,(0,0))
            else:
                layers[layers.index(layer)+1].blit(layer,(0,0))

    def shiftup():
        for layer in layers:
            if layer == latest5:
                layer.fill(clear)
            else:
                layer.fill(clear)
                layer.blit(layers[layers.index(layer)+1],(0,0))

    # Drawing static parts of overlay:
    overlay.fill(clear)

    overlaybg = overlay.copy()

    while True:

        for event in pg.event.get():

            if event.type == pg.QUIT or pg.key.get_pressed()[pg.K_ESCAPE]:
                pg.quit()
                p.terminate()
                sys.exit()

            if pg.key.get_pressed()[pg.K_RETURN]:
                pg.mouse.set_visible(True)
                pg.image.save(window, 'tmp.png')
                pg.quit()
                p.terminate()
                finalImage(sys.argv[1])
                sys.exit()

            if event.type == pg.MOUSEMOTION:
                mousepos = pg.mouse.get_pos()
                x = int(mousepos[0]*(realres[0]/screenres[0]))
                y = int(mousepos[1]*(realres[1]/screenres[1]))
                holdingclick = True
                if screenrect.collidepoint(mousepos):
                    dirtyrects.append(screenrect)

            if event.type == pg.MOUSEBUTTONDOWN:
                holdingclick = False
                if screenrect.collidepoint(mousepos):
                    dirtyrects.append(screenrect)

                # Changing brush size:
                if event.button == 4 and r < 100:
                    r += 1
                    dirtyrects.append(screenrect)
                elif event.button == 5 and r > 2:
                    r -= 1
                    dirtyrects.append(screenrect)

            if event.type == pg.KEYDOWN:

                # Emptying canvas:
                if event.key == pg.K_e:
                    #canvas.fill(white)
                    latest5.fill(clear)
                    latest4.fill(clear)
                    latest3.fill(clear)
                    latest2.fill(clear)
                    latest1.fill(clear)
                    undone = 0
                    maxundone = 0
                    dirtyrects.append(screenrect)

                # Undoing and redoing:
                if event.key == pg.K_u and undone < maxundone:
                    undone += 1
                    dirtyrects.append(screenrect)
                if event.key == pg.K_i and undone > 0:
                    undone -= 1
                    dirtyrects.append(screenrect)

        # Painting:
        if pg.mouse.get_pressed()[0] and screenrect.collidepoint(mousepos):
            if not ongoing:
                while undone > 0:
                    shiftup()
                    undone -= 1
                    maxundone -= 1
                shiftdown()
            drawline()
            ongoing = True
        else:
            startpoint = None
            if ongoing:
                if maxundone < 5:
                    maxundone += 1
                ongoing = False

        if screenrect in dirtyrects:

            # Drawing canvas:
            window.blit(bg, (0, 0))

            for layer in layers:
                if layers.index(layer) == undone:
                    window.blit(pg.transform.smoothscale(layer,(screenrect[2],screenrect[3])),screenrect)

            # Drawing overlay:
            overlay.fill(clear)
            if r > 1:
                pg.gfxdraw.aacircle(overlay,mousepos[0],mousepos[1],int(r*screenres[0]/realres[0]),black)
        overlay.blit(overlaybg,screenrect)
        window.blit(overlay,screenrect)

        pg.display.set_caption('plz draw carefully! areas are very approximate!')

        # Updating display:
        if not updated:
            pg.display.update()
            updated = True
        pg.display.update(dirtyrects)
        dirtyrects.clear()



    p.join()

if __name__ == '__main__':
    main()
