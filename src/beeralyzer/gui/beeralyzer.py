'''
Created on Nov 2, 2013

@author: jftheoret
'''

from beer_constants import A10MM_TO_05IN_CONVERSION_FACTOR
from beer_constants import A10MM_TO_SRM_CONVERSION_FACTOR
from beer_constants import EBC_TO_SRM_CONVERSION_FACTOR
from beer_constants import SRM_TO_RGB
from beer_constants import BJCP_COLOR_DESCRIPTIONS

class Beeralyzer(object):

    def __init__(self):
        pass

    ''' 
        From Beer-10 of ASBC MOA
        Determines if a sample is clear enough for 
    '''
    def isTurbid(self, a430_10mm, a700_10mm):
        a430_05in = a430_10mm * A10MM_TO_05IN_CONVERSION_FACTOR
        a700_05in = a700_10mm * A10MM_TO_05IN_CONVERSION_FACTOR
        
        return a700_05in > 0.039 * a430_05in
    
    def getSRM(self, a430_10mm, dilution=1):
        return A10MM_TO_SRM_CONVERSION_FACTOR * a430_10mm * dilution
    
    def getEBC(self, a430_10mm, dilution=1):
        return (self.getSRM(a430_10mm, dilution) * EBC_TO_SRM_CONVERSION_FACTOR)
    
    def getDilutionValue(self, dilution):
        if dilution == 'None':
            return 1
        elif dilution == "1:1":
            return 2
        elif dilution == "1:2":
            return 3
        else:
            return 1
        
    def getDescriptionFromSRM(self, SRM):
        description = ''
        for item in BJCP_COLOR_DESCRIPTIONS:
            srmMin = item[0]
            srmMax = item[1]
            if SRM >= srmMin and SRM < srmMax:
                description = item[2]
                break
        return description
    
    def getRGBfromSRM(self, SRM):
        R = 0
        G = 0
        B = 0
        found = False
        for item in SRM_TO_RGB:
            if item[0] >= SRM:
                R = item[1]
                G = item[2]
                B = item[3]
                found = True
                break
        if not found:
            R=G=B=0
        return R, G, B
    
