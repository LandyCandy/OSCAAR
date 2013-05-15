'''
Generate sample data to test oscaar with.

Compile and run with: 
    % gcc -shared -o c/transit1forLMLS.so c/transit1forLMLS.c -framework Python ; python generateSampleData.py


Core developer: Brett Morris
'''

import numpy as np
import pyfits
from matplotlib import pyplot as plt
import generateModelLC as genModel

NdataImages = 200          ## Number of data images to generate
NdarkImages = 3          ## Number of dark frames to generate
NflatImages = 3          ## Number of flat fields to generate
imageDimensionX = 120     ## pixel dimensions of each image
imageDimensionY = 40
starDimensions = 4       ## pixel dimensions of the stars
skyBackground = 500      ## background counts from sky brightness
darkBackground = 100     ## background counts from detector

import os; os.system('rm images/*')

## Pixel positions of the stars (x,y)
targetX = [20-starDimensions/2,20+starDimensions/2]
compAX = [60-starDimensions/2,60+starDimensions/2]
compBX = [100-starDimensions/2,100+starDimensions/2]
starsY = [imageDimensionY/2-starDimensions/2,imageDimensionY/2+starDimensions/2]

## Set times, model params
jd0 = 2456427.88890
exposureTime = 45/(60*60*24.) ## Convert s -> hr
#times = np.arange(jd0,jd0+exposureTime*NdataImages,exposureTime)/ 1.580400
#times -= np.mean(times)
# [p,ap,P,i,gamma1,gamma2,e,longPericenter,t0,percentOfOrbit]
times = np.arange(jd0,jd0+exposureTime*NdataImages,exposureTime)
print np.mean(times,dtype=np.float64)
modelParams = [ 0.1179, 14.71, 1.580400, 90.0, 0.23, \
                0.30, 0.00, 0.0, np.mean(times,dtype=np.float64), 2.0]
print times
modelLightCurve = genModel.simulateLC(times,modelParams)
plt.plot(times,modelLightCurve)
plt.show()

## Simulate dark frames with shot noise
for i in range(NdarkImages):
    darkFrame = darkBackground + np.random.normal(np.zeros([imageDimensionY,imageDimensionX]),np.sqrt(darkBackground))
    darkFrame = np.require(darkFrame,dtype=int)   ## Require integer counts
    pyfits.writeto('images/simulatedImg-'+str(i).zfill(3)+'d.fits',darkFrame)

## Simulate ideal flat frames (perfectly flat)
for i in range(NflatImages):
    ## Flats will be completely flat -- ie, we're pretending that we have a 
    ##      perfect optical path with no variations.
    flatField = np.ones([imageDimensionY,imageDimensionX],dtype=np.int) ## Require integer counts
    pyfits.writeto('images/simulatedImg-'+str(i).zfill(3)+'f.fits',flatField)

## Create data images
for i in range(0,NdataImages):
    ## Produce image with sky and dark background with simulated photon noise for each source
    simulatedImage = darkBackground +\
        np.random.normal(np.zeros([imageDimensionY,imageDimensionX]),np.sqrt(darkBackground)) + skyBackground +\
        np.random.normal(np.zeros([imageDimensionY,imageDimensionX]),np.sqrt(skyBackground))
    
    ## Create two box-shaped stars with simulated photon noise
    targetBrightness = 3000*modelLightCurve[i]  ## Scale brightness with the light curve
    target = targetBrightness +\
        np.random.normal(np.zeros([starDimensions,starDimensions]),np.sqrt(targetBrightness))
    
    compBrightnessA = 2500
    compBrightnessB = 2700
    compA = compBrightnessA +\
        np.random.normal(np.zeros([starDimensions,starDimensions]),np.sqrt(compBrightnessA))
    compB = compBrightnessB +\
        np.random.normal(np.zeros([starDimensions,starDimensions]),np.sqrt(compBrightnessB))
    
    
    ## Add stars onto the simulated image
    simulatedImage[starsY[0]:starsY[1],targetX[0]:targetX[1]] += target
    simulatedImage[starsY[0]:starsY[1],compAX[0]:compAX[1]] += compA
    simulatedImage[starsY[0]:starsY[1],compBX[0]:compBX[1]] += compB

    ## Force counts to integers, save.
    #simulatedImage = np.transpose(simulatedImage)
    simulatedImage = np.require(simulatedImage,dtype=int)   ## Require integer counts before save

    header = pyfits.Header()
    header.append(('JD',times[i],'Simulated Time (Julian Date)'))
    pyfits.writeto('images/simulatedImg-'+str(i).zfill(3)+'r.fits',simulatedImage,header=header)