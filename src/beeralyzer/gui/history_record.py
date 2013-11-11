'''
Created on Nov 7, 2013

@author: jftheoret
'''

import time
import datetime
from collections import OrderedDict
from beer_constants import COLOR_UNITS
from beer_constants import TURBIDITY_UNITS
from beer_constants import DILUTION_VALUES

DATE_KEY            = 'date'
TIME_KEY            = 'time'
OPERATOR_KEY        = 'operator'
GYLE_KEY            = 'gyle'
SAMPLE_KEY          = 'sampleType'
DILUTION_KEY        = 'dilution'
COLOR_KEY           = 'color'
COLOR_UNITS_KEY     = 'colorUnits'
TURBIDITY_KEY       = 'turbidity'
TURBIDITY_UNITS_KEY = 'turbidityUnits'
MIN_COLOR_KEY       = 'minColorSpec'
MAX_COLOR_KEY       = 'maxColorSpec'
MIN_TURBIDITY_KEY   = 'minTurbiditySpec'
MAX_TURBIDITY_KEY   = 'maxTurbiditySpec'
NOTES_KEY           = 'notes'

class BeeralyzerHistoryRecord(object):

    def __init__(self):
        
        self.data = OrderedDict([(DATE_KEY,            ['Date', datetime.date.today()]),
                                 (TIME_KEY,            ['Time', time.time()]),
                                 (OPERATOR_KEY,        ['Operator', '']),
                                 (GYLE_KEY,            ['Gyle', '']),
                                 (SAMPLE_KEY,          ['Sample', '']),
                                 (DILUTION_KEY,        ['Dilution', DILUTION_VALUES[1]]),
                                 (COLOR_KEY,           ['Color', 0.0]),
                                 (COLOR_UNITS_KEY,     ['Color Units', COLOR_UNITS[0]]),
                                 (TURBIDITY_KEY,       ['Turbidity', 0.0]),
                                 (TURBIDITY_UNITS_KEY, ['Turbidity Units', TURBIDITY_UNITS[0]]),
                                 (MIN_COLOR_KEY,       ['Min Color Spec', 0.0]),
                                 (MAX_COLOR_KEY,       ['Max Color Spec', float("inf")]),
                                 (MIN_TURBIDITY_KEY,   ['Min Turb. Spec', 0.0]),
                                 (MAX_TURBIDITY_KEY,   ['Max Turb. Spec', 0.0]),
                                 (NOTES_KEY,           ['Notes',''])])
                                
    def getDescriptions(self):
        descriptions = []
        for item in self.data.itervalues():
            descriptions.append(item[0])
        return descriptions
        
    def setDate(self, date):
        self.data.get(DATE_KEY)[1] = date

    def setTime(self, time):
        self.data.get(TIME_KEY)[1] = time
    
    def setOperator(self, operator):
        self.data.get(OPERATOR_KEY)[1] = operator
        
    def setGyle(self, gyle):
        self.data.get(GYLE_KEY)[1] = gyle

    def setSample(self, sample):
        self.data.get(SAMPLE_KEY)[1] = sample

    def setDilution(self, dilution):
        self.data.get(DILUTION_KEY)[1] = dilution

    def setColor(self, color):
        self.data.get(COLOR_KEY)[1] = color
 
    def setColorUnits(self, colorUnits):
        self.data.get(COLOR_UNITS_KEY)[1] = colorUnits

    def setTurbidity(self, turbidity):
        self.data.get(TURBIDITY_KEY)[1] = turbidity
    
    def setTurbidityUnits(self, turbidity):
        self.data.get(TURBIDITY_UNITS_KEY)[1] = turbidity

    def setMinColor(self, minColor):
        self.data.get(MIN_COLOR_KEY)[1] = minColor

    def setMaxColor(self, maxColor):
        self.data.get(MAX_COLOR_KEY)[1] = maxColor

    def setMinTurbidity(self, minTurbidity):
        self.data.get(MIN_TURBIDITY_KEY)[1] = minTurbidity 

    def setMaxTurbidity(self, maxTurbidity):
        self.data.get(MAX_TURBIDITY_KEY)[1] = maxTurbidity

    def setNotes(self, notes):
        self.data.get(NOTES_KEY)[1] = notes
        
    def getKey(self):
        return str(self.data.get(DATE_KEY)[1]) + str(self.data.get(TIME_KEY)[1])
    
    def toList(self):
        result = []

        for value in self.data.itervalues():
            result.append(value[1])
        
        return result
