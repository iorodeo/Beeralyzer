'''
Created on Nov 2, 2013

@author: jftheoret
'''
import ConfigParser

COMM_SECTION     = "Communications"
PORT_NAME        = "PortName"
PORT_AUTOCONNECT = "AutoConnect"

SAMPLE_SECTION   = "Samples"
SAMPLE_DIGITS    = "NumberOfDigits"

CONFIRM_SECTION  = "Confirmations"
ON_EXIT          = "OnExit"
ON_HIST_DELETE   = "OnHistoryDelete"
ON_RECALIBRATE   = "OnRecalibrate"

class BeeralyzerConfigFile(object):
    config = ConfigParser.RawConfigParser()
    configFileName = 'beeralyzer.cfg'
        
    serialPortName         = ''
    autoConnect            = False
    significantDigits      = 4

    confirmOnExit          = True
    confirmOnRecal         = True
    confirmOnDeleteHistory = True
        
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

    def save(self):
        try:
            self.config.add_section(COMM_SECTION)
            self.config.add_section(SAMPLE_SECTION)
            self.config.add_section(CONFIRM_SECTION)
        except Exception:
            pass
            
        self.config.set(COMM_SECTION,   PORT_NAME,        self.serialPortName)
        self.config.set(COMM_SECTION,   PORT_AUTOCONNECT, self.autoConnect)
        self.config.set(SAMPLE_SECTION, SAMPLE_DIGITS,    self.significantDigits)
 
        self.config.set(CONFIRM_SECTION, ON_EXIT,        self.confirmOnExit)
        self.config.set(CONFIRM_SECTION, ON_RECALIBRATE, self.confirmOnRecal)
        self.config.set(CONFIRM_SECTION, ON_HIST_DELETE, self.confirmOnDeleteHistory)
        
        with open(self.configFileName, 'wb') as configfile:
            self.config.write(configfile)
    
    def load(self):
        try:
            self.config.read(self.configFileName)
            self.autoConnect = self.config.getboolean(COMM_SECTION, PORT_AUTOCONNECT)
            self.serialPortName = self.config.get(COMM_SECTION, PORT_NAME)
            self.significantDigits = self.config.getint(SAMPLE_SECTION, SAMPLE_DIGITS)
            self.confirmOnExit = self.config.getboolean(CONFIRM_SECTION, ON_EXIT)
            self.confirmOnRecal = self.config.getboolean(CONFIRM_SECTION, ON_RECALIBRATE)
            self.confirmOnDeleteHistory = self.config.getboolean(CONFIRM_SECTION, ON_HIST_DELETE)
            return True
        except IOError:
            return False 
            
    