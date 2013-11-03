'''
Created on Oct 26, 2013

@author: jftheoret
'''
import sys

from PyQt4 import QtGui
from PyQt4 import uic
from colorimeter.colorimeter_serial import Colorimeter
import platform
import colorimeter.constants
from beeralyzer import Beeralyzer
from beeralyzer_config import BeeralyzerConfigFile
import numpy.random
from portfolio import BeerPortfolio

DEBUG = False

class beeralyzerGui(QtGui.QMainWindow):
    
    config = BeeralyzerConfigFile()
    
    def __init__(self, parent=None):
        super(beeralyzerGui,self).__init__(parent)
        QtGui.QMainWindow.__init__(self)
        self.ui = uic.loadUi("mainwindow.ui", self)

        self.portfolio = BeerPortfolio()        
        
        self.connectActions()
        self.initialize()
        self.updateWidgetEnabled()
        self.beeralyzer = Beeralyzer()
        self.center()
        self.show()
    
    def closeEvent(self, event):
        title = "Message"
        message = "Do you really want to quit?"
        reply = QtGui.QMessageBox.question(self, title, message, QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
            if not self.dev is None:
                self.disconnectDevice()
        else:
            event.ignore()  

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
            
    def initialize(self):
        self.isCalibrated = False
        self.dev = None
        self.numSamples = None
        
        self.a430 = 0.0
        self.a700 = 0.0

        self.statusbar.showMessage('Not Connected')
        
        self.populateSerialPortComboBox()
        self.loadConfiguration() 
        self.loadPortfolioData()       
            
    def populateSerialPortComboBox(self):
        try:
            from serial.tools.list_ports import comports
        except ImportError:
                comports = None
        
        osType = platform.system()
        if comports:
            for p in sorted(comports()):
                self.serialPortCombo.addItem(p[0])
            self.port = self.serialPortCombo.itemText(0)    
        elif osType == 'Linux': 
            self.port = colorimeter.constants.DFLT_PORT_LINUX 
        elif osType == 'Darwin':
            self.port = colorimeter.constants.DFLT_PORT_DARWIN
        else: 
            self.port = colorimeter.constants.DFLT_PORT_WINDOWS 

    def loadConfiguration(self):
        if self.config.load():
            self.significantDigitsSpinBox.setValue(self.config.significantDigits)
            self.autoConnectCheckBox.setChecked(self.config.autoConnect)
            index = self.serialPortCombo.findText(self.config.serialPortName)
            if index != -1:
                self.serialPortCombo.setCurrentIndex(index)
                if self.config.autoConnect:
                    self.connectDevice()

    def loadPortfolioData(self):
        portfolioNameList = self.portfolio.list()
        portfolioNameList.sort()
        self.beerNameComboBox.clear()
        for key in portfolioNameList:
            self.beerNameComboBox.addItem(key)
            self.currentMeasurementPortfolioComboBox.addItem(key)
        self.updatePortfolioInfo()

    def updatePortfolioInfo(self):
        currentPortfolioName = self.beerNameComboBox.currentText()
        selectedItem = self.portfolio.get(str(currentPortfolioName))
        if selectedItem is not None:
            index = self.BJCPStyleComboBox.findText(selectedItem.style)
            if index != -1:
                self.BJCPStyleComboBox.setCurrentIndex(index)
            self.minColorSpecLineEdit.setText(self.floatToString(selectedItem.minColor))
            self.maxColorSpecLineEdit.setText(self.floatToString(selectedItem.maxColor))
            self.minTurbiditySpecLineEdit.setText(self.floatToString(selectedItem.minTurbidity))
            self.maxTurbiditySpecLineEdit.setText(self.floatToString(selectedItem.maxTurbidity))
    
    def updateSelectedMeasurementPortfolioInfo(self):
        currentPortfolioName = self.currentMeasurementPortfolioComboBox.currentText()
        selectedItem = self.portfolio.get(str(currentPortfolioName))
        if selectedItem is not None:
            self.currentMinColorSpecLabel.setText(self.floatToString(selectedItem.minColor))
            self.currentMaxColorSpecLabel.setText(self.floatToString(selectedItem.maxColor))
            self.currentMinTurbiditySpecLabel.setText(self.floatToString(selectedItem.minTurbidity))
            self.currentMaxTurbiditySpecLabel.setText(self.floatToString(selectedItem.maxTurbidity))

    def connectActions(self):
        self.serialPortCombo.editTextChanged.connect(self.portChanged_Callback)
        self.connectPushButton.pressed.connect(self.connectPressed_Callback)
        self.connectPushButton.clicked.connect(self.connectClicked_Callback)

        self.calibratePushButton.pressed.connect(self.calibratePressed_Callback)
        self.calibratePushButton.clicked.connect(self.calibrateClicked_Callback)
        self.measurePushButton.clicked.connect(self.measureClicked_Callback)
        self.measurePushButton.pressed.connect(self.measurePressed_Callback)

        self.reloadSerialPortListButton.clicked.connect(self.reloadSerialPortListClicked_Callback)
        
        self.saveConfigPushButton.clicked.connect(self.saveConfigClicked_Callback)
        self.savePortfolioItemPushButton.clicked.connect(self.savePortfolioItemClicked_Callback)
        self.deletePortfolioItemPushButton.clicked.connect(self.deletePortfolioItemClicked_Callback)
        
        self.beerNameComboBox.editTextChanged.connect(self.updatePortfolioInfo)
        self.currentMeasurementPortfolioComboBox.currentIndexChanged.connect(self.updateSelectedMeasurementPortfolioInfo)
        
    def reloadSerialPortListClicked_Callback(self):
        self.serialPortCombo.clear()
        self.populateSerialPortComboBox()

    def getMeasurement(self):
        
        if DEBUG:
            self.a430 = numpy.random.random()
            self.a700 = numpy.random.random()
            return
        
        error = False
        try:
            srmFreq, srmTrans, srmAbso = self.dev.getMeasurementBlue()
            turbidityFreq, turbidityTrans, turbidityAbso = self.dev.getMeasurementGreen()
        except IOError: 
            msgTitle = 'Measurement Error:'
            msgText = 'unable to get measurement'
            QtGui.QMessageBox.warning(self,msgTitle, msgText)
            error = True
        if error:
            self.a430 = self.a700 = None
        else:
            self.a430 = srmAbso
            self.a700 = turbidityAbso

    def connectPressed_Callback(self):
        if self.dev is None:
            self.serialPortCombo.setEnabled(False)
            self.statusbar.showMessage('Connecting...')

    def portChanged_Callback(self):
        self.port = str(self.serialPortCombo.currentText())

    def connectClicked_Callback(self):
        if self.dev is None:
            self.connectDevice()
        else:
            self.disconnectDevice()
        self.updateWidgetEnabled()

    def connectDevice(self):
        try:
            self.dev = Colorimeter(self.port)
            self.numSamples = self.dev.getNumSamples()
        except Exception, e:
            msgTitle = 'Connection Error'
            msgText = 'unable to connect to device: {0}'.format(str(e))
            QtGui.QMessageBox.warning(self,msgTitle, msgText)
            self.statusbar.showMessage('Not Connected')
            self.dev = None
        if self.dev is not None:
            self.samplesLineEdit.setText('{0}'.format(self.numSamples))
            self.dev.setSensorModeColorIndependent()

    def disconnectDevice(self):
        try:
            self.cleanUpAndCloseDevice()
        except Exception, e:
            QtGui.QMessageBox.critical(self,'Error', str(e))
        self.samplesLineEdit.setText('')

    def cleanUpAndCloseDevice(self):
        if not colorimeter.constants.DEVEL_FAKE_MEASURE:    
            self.dev.close()
        self.dev = None

    def updateWidgetEnabled(self):
        
        if DEBUG:
            return
        
        if self.dev is None:
            self.connectPushButton.setText('Connect')
            self.samplesLineEdit.setEnabled(False)
            self.measurePushButton.setEnabled(False)
            self.calibratePushButton.setEnabled(False)
            self.statusbar.showMessage('Not Connected')
            self.serialPortCombo.setEnabled(True)
        else:
            self.connectPushButton.setText('Disconnect')
            if self.isCalibrated:
                self.measurePushButton.setEnabled(True)
            else:
                self.measurePushButton.setEnabled(False)
            self.samplesLineEdit.setEnabled(True)
            self.serialPortCombo.setEnabled(False)
            self.statusbar.showMessage('Connected, Stopped')
            self.calibratePushButton.setEnabled(True)
            
    def calibratePressed_Callback(self):
        self.measurePushButton.setEnabled(False)
        self.statusbar.showMessage('Connected, Calibrating...')

    def calibrateClicked_Callback(self):
        try:
            self.dev.calibrateBlue()
            self.dev.calibrateGreen()
            self.isCalibrated = True
        except IOError, e:
            msgTitle = 'Calibration Error:'
            msgText = 'unable to calibrate device: {0}'.format(str(e))
            QtGui.QMessageBox.warning(self,msgTitle, msgText)
            self.updateWidgetEnabled()
        self.updateWidgetEnabled()

    def measurePressed_Callback(self):
        self.calibratePushButton.setEnabled(False)
        self.statusbar.showMessage('Connected, Measuring...')

    def measureClicked_Callback(self):
        self.getMeasurement()
        self.displayMeasurements()
        self.updateWidgetEnabled()       

    def floatToString(self, floatValue):
        return '{value:1.{digits}f}'.format(value=floatValue,digits=self.significantDigitsSpinBox.value())
          
    def displayMeasurements(self):
        dilutionRatio = self.beeralyzer.getDilutionValue(self.dilutionComboBox.currentText())
        srmValue = self.beeralyzer.getSRM(self.a430, dilutionRatio)
        self.colorLineEdit.setText(self.floatToString(srmValue))
        self.turbidityLineEdit.setText(self.floatToString(self.a700))
        self.setColorTextColor(self.a430, self.a700)
        self.setBeerColorPreview(srmValue)
        self.setBeerColorDescription(srmValue)
    
    def setColorTextColor(self, a430_10mm, a700_10mm):
        editor = self.colorLineEdit
        palette = editor.palette()
        if self.beeralyzer.isTurbid(a430_10mm, a700_10mm):
            palette.setColor(QtGui.QPalette.Active, QtGui.QPalette.Text, QtGui.QColor(255, 0, 0))
        else:
            palette.setColor(QtGui.QPalette.Active, QtGui.QPalette.Text, QtGui.QColor(0, 0, 0))
        editor.setPalette(palette)

    def setBeerColorPreview(self, srmValue):
        R, G, B = self.beeralyzer.getRGBfromSRM(srmValue)
        palette = self.colorPreviewEdit.palette()
        palette.setColor(QtGui.QPalette.Active, QtGui.QPalette.Base, QtGui.QColor(R, G, B))
        self.colorPreviewEdit.setPalette(palette)

    def setBeerColorDescription(self, srmValue):
        self.BJCPColorDescriptionLineEdit.setText(self.beeralyzer.getDescriptionFromSRM(srmValue))

    def saveConfigClicked_Callback(self):
        self.config.setPortName(self.serialPortCombo.currentText())
        self.config.setAutoConnect(self.autoConnectCheckBox.isChecked())
        self.config.setSignificantDigits(self.significantDigitsSpinBox.value())
        self.config.save()
        
    def savePortfolioItemClicked_Callback(self):
        self.portfolio.add(str(self.beerNameComboBox.currentText()),
                           str(self.BJCPStyleComboBox.currentText()),
                           float(self.minColorSpecLineEdit.text()),
                           float(self.maxColorSpecLineEdit.text()),
                           float(self.minTurbiditySpecLineEdit.text()),
                           float(self.maxTurbiditySpecLineEdit.text()))

    def deletePortfolioItemClicked_Callback(self):
        self.portfolio.delete(self.beerNameComboBox.currentText())
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myApp = beeralyzerGui()
    sys.exit(app.exec_())