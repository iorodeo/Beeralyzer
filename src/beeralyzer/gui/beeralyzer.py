'''
Created on Nov 2, 2013

@author: jftheoret
'''

from beer_constants import A10MM_TO_05IN_CONVERSION_FACTOR
from beer_constants import A10MM_TO_SRM_CONVERSION_FACTOR
from beer_constants import EBC_TO_SRM_CONVERSION_FACTOR
from beer_constants import SRM_TO_RGB
from beer_constants import BJCP_COLOR_DESCRIPTIONS
from beer_constants import COLOR_UNITS
from beer_constants import DILUTION_VALUES
from beer_constants import TURBIDITY_UNITS

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
    
    def getAbsorbance(self, a430_10mm, dilution=1):
        return a430_10mm * dilution
    
    def getDilutionValue(self, dilution):
        for key, value in DILUTION_VALUES.items():
            if dilution == value:
                return key    
        return 0
        
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
    
    def isColorInRange(self, a430, dilution, minSpec, maxSpec, units=COLOR_UNITS[0]):
        if units == COLOR_UNITS[0]:
            d = self.getDilutionValue(dilution)
            srm = self.getSRM(a430, d)
            if (srm >= minSpec) and (srm <= maxSpec):
                return True
            else:
                return False
        else:
            #TODO: Implement other units!
            return False
        
    def isTurbidityInRange(self, a700, minSpec, maxSpec, units=TURBIDITY_UNITS[0]):
        if units == TURBIDITY_UNITS[0]:
            if (a700 >= minSpec) and (a700 <= maxSpec):
                return True
            else:
                return False
        else:
            #TODO: Implement other units!
            return False
