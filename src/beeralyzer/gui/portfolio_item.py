'''
Created on Nov 3, 2013

@author: jftheoret
'''

class BeerPortfolioItem(object):

    def __init__(self, name='', style='', minColor=0.0, maxColor=99.9, minTurbidity=0.0, maxTurbidity=99.9):
        self.name                = name
        self.style               = style
        self.minColor            = minColor
        self.maxColor            = maxColor
        self.minTurbidity        = minTurbidity
        self.maxTurbidity        = maxTurbidity
        self.lastMeasuredValues  = '---'
        self.lastMeasurementDate = 'Never'
        