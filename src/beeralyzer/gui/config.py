'''
Created on Nov 2, 2013

@author: jftheoret
'''
import os
import sys
import ConfigParser
from constants import BEERALYZER_DIRECTORY
from resource_path import resourcePath

COMM_SECTION          = "Communications"
PORT_NAME             = "PortName"
PORT_AUTOCONNECT      = "AutoConnect"

SAMPLE_SECTION        = "Samples"
SAMPLE_DIGITS         = "NumberOfDigits"

CONFIRM_SECTION       = "Confirmations"
ON_EXIT               = "OnExit"
ON_HIST_DELETE        = "OnHistoryDelete"
ON_RECALIBRATE        = "OnRecalibrate"

LOOK_FEEL_SECTION     = "LookAndFeel"
HISTORY_TBL_FONT      = "HistoryTableFontFamily"
HISTORY_TBL_FONT_SIZE = "HistoryTableFontSize"

DEFAULT_UNITS_SECTION = "DefaultUnits"
DEFAULT_COLOR_UNITS   = "Color"
DEFAULT_TURB_UNITS    = "Turbidity"

class BeeralyzerConfigFile(object):

    def __init__(self):
        self.config = ConfigParser.RawConfigParser()

        self.configFileName = 'beeralyzer.cfg'
        self.configFileFullPath = os.path.join(BEERALYZER_DIRECTORY, self.configFileName) 

        self.defaultConfigFileName =  'default_beeralyzer.cfg'
        self.defaultConfigFileFullPath = resourcePath(self.defaultConfigFileName) 
            
        self.serialPortName         = ''
        self.autoConnect            = False
        self.significantDigits      = 4
        self.confirmOnExit          = True
        self.confirmOnRecal         = True
        self.confirmOnDeleteHistory = True

        self.historyFontFamily      = "Courier New"
        self.historyFontSize        = 10
        
        self.defaultColorUnits      = ''
        self.defaultTurbidityUnits  = ''
        
    def setPortName(self, portName):
        self.serialPortName = portName    
    
    def setAutoConnect(self, autoConnect):
        self.autoConnect = autoConnect
        
    def setSignificantDigits(self, digits):
        self.significantDigits = digits
        
    def setConfirmOnExit(self, confirm):
        self.confirmOnExit = confirm
        
    def setConfirmOnRecal(self, confirm):
        self.confirmOnRecal = confirm

    def setConfirmOnDeleteHistory(self, confirm):
        self.confirmOnDeleteHistory = confirm

    def setHistoryFont(self, family, size):
        self.historyFontFamily = family
        self.historyFontSize = size

    def setDefaultColorUnits(self, units):
        self.defaultColorUnits = units

    def setDefaultTurbidityUnits(self, units):
        self.defaultTurbidityUnits = units

    def save(self):
        try:
            self.config.add_section(COMM_SECTION)
            self.config.add_section(SAMPLE_SECTION)
            self.config.add_section(CONFIRM_SECTION)
            self.config.add_section(LOOK_FEEL_SECTION)
            self.config.add_section(DEFAULT_UNITS_SECTION)
        except Exception:
            pass
            
        self.config.set(COMM_SECTION,   PORT_NAME,        self.serialPortName)
        self.config.set(COMM_SECTION,   PORT_AUTOCONNECT, self.autoConnect)
        self.config.set(SAMPLE_SECTION, SAMPLE_DIGITS,    self.significantDigits)
 
        self.config.set(CONFIRM_SECTION, ON_EXIT,        self.confirmOnExit)
        self.config.set(CONFIRM_SECTION, ON_RECALIBRATE, self.confirmOnRecal)
        self.config.set(CONFIRM_SECTION, ON_HIST_DELETE, self.confirmOnDeleteHistory)
        
        self.config.set(LOOK_FEEL_SECTION, HISTORY_TBL_FONT,      self.historyFontFamily)
        self.config.set(LOOK_FEEL_SECTION, HISTORY_TBL_FONT_SIZE, self.historyFontSize)
        
        self.config.set(DEFAULT_UNITS_SECTION, DEFAULT_COLOR_UNITS, self.defaultColorUnits)
        self.config.set(DEFAULT_UNITS_SECTION, DEFAULT_TURB_UNITS,  self.defaultTurbidityUnits)

        with open(self.configFileFullPath, 'wb') as configfile:
            self.config.write(configfile)
    
    def load(self):
        if os.path.exists(self.configFileFullPath):
            fullPathName = self.configFileFullPath
        else:
            fullPathName = self.defaultConfigFileFullPath
        try:
            self.config.read(fullPathName)
            self.autoConnect            = self.config.getboolean(COMM_SECTION, PORT_AUTOCONNECT)
            self.serialPortName         = self.config.get(COMM_SECTION, PORT_NAME)
            self.significantDigits      = self.config.getint(SAMPLE_SECTION, SAMPLE_DIGITS)
            self.confirmOnExit          = self.config.getboolean(CONFIRM_SECTION, ON_EXIT)
            self.confirmOnRecal         = self.config.getboolean(CONFIRM_SECTION, ON_RECALIBRATE)
            self.confirmOnDeleteHistory = self.config.getboolean(CONFIRM_SECTION, ON_HIST_DELETE)
            self.historyFontFamily      = self.config.get(LOOK_FEEL_SECTION, HISTORY_TBL_FONT)
            self.historyFontSize        = self.config.getint(LOOK_FEEL_SECTION, HISTORY_TBL_FONT_SIZE)
            self.defaultColorUnits      = self.config.get(DEFAULT_UNITS_SECTION, DEFAULT_COLOR_UNITS)
            self.defaultTurbidityUnits  = self.config.get(DEFAULT_UNITS_SECTION, DEFAULT_TURB_UNITS)
            return True
        except IOError:
            return False 
            
    
