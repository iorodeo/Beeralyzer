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

class BeeralyzerConfigFile(object):
    serialPortName = ''
    autoConnect = False
    significantDigits = 4
    config = ConfigParser.RawConfigParser()
    configFileName = 'beeralyzer.cfg'
        
    def setPortName(self, portName):
        self.serialPortName = portName    
    
    def setAutoConnect(self, autoConnect):
        self.autoConnect = autoConnect
        
    def setSignificantDigits(self, digits):
        self.significantDigits = digits
        
    def save(self):
        try:
            self.config.add_section(COMM_SECTION)
            self.config.add_section(SAMPLE_SECTION)
        except Exception:
            pass
            
        self.config.set(COMM_SECTION, PORT_NAME, self.serialPortName)
        self.config.set(COMM_SECTION, PORT_AUTOCONNECT, self.autoConnect)
        self.config.set(SAMPLE_SECTION, SAMPLE_DIGITS, self.significantDigits)
        with open(self.configFileName, 'wb') as configfile:
            self.config.write(configfile)
    
    def load(self):
        try:
            self.config.read(self.configFileName)
            self.autoConnect = self.config.getboolean(COMM_SECTION, PORT_AUTOCONNECT)
            self.serialPortName = self.config.get(COMM_SECTION, PORT_NAME)
            self.significantDigits = self.config.getint(SAMPLE_SECTION, SAMPLE_DIGITS)
            return True
        except IOError:
            return False 
            
    