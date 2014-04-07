'''
Created on Oct 26, 2013

@author: jftheoret
'''
import platform
import sys
import os


from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import QFont
from PyQt4.QtGui import QFontDialog
from PyQt4.QtGui import QDoubleValidator
from colorimeter.colorimeter_serial import Colorimeter
import colorimeter.constants
from numpy import recfromcsv

from about_gui import AboutWindow
from beer_constants import COLOR_UNITS, DILUTION_VALUES, TURBIDITY_UNITS
from beeralyzer import Beeralyzer
from config import BeeralyzerConfigFile
from constants import VERSION
from constants import BEERALYZER_DIRECTORY
from history_file import HistoryFile
from history_record import BeeralyzerHistoryRecord
from history_tablemodel import BeeralyzerTableModel
from measure_notes import MeasureNotes
from portfolio import BeerPortfolio
from resource_path import resourcePath
import images_rc

TEST= False

class BeeralyzerGui(QtGui.QMainWindow):
    
    config = BeeralyzerConfigFile()
    
    def __init__(self, parent=None):
        super(BeeralyzerGui,self).__init__(parent)
        QtGui.QMainWindow.__init__(self)
        self.ui = uic.loadUi(resourcePath("mainwindow.ui"), self)
        self.checkForBeeralyzerDir()

        self.portfolio = BeerPortfolio()        
        self.beeralyzer = Beeralyzer()

        self.initialize()
        self.connectActions()
        self.updateWidgetEnabled()
        self.center()
        self.show()
    
    def closeEvent(self, event):
        if self.config.confirmOnExit:
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
        else:
            if not self.dev is None:
                self.disconnectDevice()
           
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
            
    def initialize(self):
        self.isCalibrated = False
        self.dev = None
        self.numSamples = None


        self.history = HistoryFile()
        self.tablemodel = None
        
        self.currentNotes = ''
        
        self.a430 = 0.0
        self.a700 = 0.0
        
        self.historTableFontFamily = "Courier New"
        self.historyTableFontSize = 10
        
        self.statusbar.showMessage('Not Connected')
        self.version = VERSION
        self.setWindowTitle("Beeralyzer - Version " + VERSION)        
        
        self.colorOOSLabel.hide()
        self.turbidityOOSLabel.hide()
        
        self.minColorSpecLineEdit.setValidator(QDoubleValidator())
        self.maxColorSpecLineEdit.setValidator(QDoubleValidator())
        self.minTurbiditySpecLineEdit.setValidator(QDoubleValidator())
        self.maxTurbiditySpecLineEdit.setValidator(QDoubleValidator())
        
        self.populateSerialPortComboBox()
        self.populateMeasurementUnits()
        self.loadConfiguration() 
        self.loadPortfolioData()   
        self.loadBJCPData()   
        self.loadHistoryData()
        self.dateTimeEdit.setDateTime(QtCore.QDateTime.currentDateTime())
             
    def populateSerialPortComboBox(self):
        try:
            from serial.tools.list_ports import comports
        except ImportError:
                comports = None
        
        osType = platform.system()
        if comports:
            for p in sorted(comports()):
                self.serialPortCombo.addItem(p[0])
#            self.port = self.serialPortCombo.itemText(0)    
        elif osType == 'Linux': 
            self.port = colorimeter.constants.DFLT_PORT_LINUX 
        elif osType == 'Darwin':
            self.port = colorimeter.constants.DFLT_PORT_DARWIN
        else: 
            self.port = colorimeter.constants.DFLT_PORT_WINDOWS 

    def populateMeasurementUnits(self):
        self.colorMeasurementUnitCombobox.clear()
        self.turbidityMeasurementUnitComboBox.clear()
        self.dilutionCombobox.clear()
        self.defaultColorUnitsCombobox.clear()
        self.defaultTurbidityUnitsCombobox.clear()

        for value in COLOR_UNITS.itervalues():
            self.colorMeasurementUnitCombobox.addItem(value)
            self.defaultColorUnitsCombobox.addItem(value)
        for value in TURBIDITY_UNITS.itervalues():
            self.turbidityMeasurementUnitComboBox.addItem(value)
            self.defaultTurbidityUnitsCombobox.addItem(value)
        for value in DILUTION_VALUES.itervalues():
            self.dilutionCombobox.addItem(value)

    def loadConfiguration(self):
        if self.config.load():
            self.significantDigitsSpinBox.setValue(self.config.significantDigits)
            self.autoConnectCheckbox.setChecked(self.config.autoConnect)

            self.confirmOnExitCheckbox.setChecked(self.config.confirmOnExit)
            self.confirmOnRecalibrateCheckbox.setChecked(self.config.confirmOnRecal)
            self.confirmOnHistoryDeleteCheckbox.setChecked(self.config.confirmOnDeleteHistory)
            
            self.historTableFontFamily = self.config.historyFontFamily
            self.historTableFontSize = self.config.historyFontSize
            
            index = self.serialPortCombo.findText(self.config.serialPortName)
            if index != -1:
                self.serialPortCombo.setCurrentIndex(index)
                self.port = self.config.serialPortName
                if self.config.autoConnect:
                    self.connectDevice()

            index = self.defaultColorUnitsCombobox.findText(self.config.defaultColorUnits)
            if index != -1:
                self.defaultColorUnitsCombobox.setCurrentIndex(index)
                self.colorMeasurementUnitCombobox.setCurrentIndex(index)

            index = self.defaultTurbidityUnitsCombobox.findText(self.config.defaultTurbidityUnits)
            if index != -1:
                self.defaultTurbidityUnitsCombobox.setCurrentIndex(index)
                self.turbidityMeasurementUnitComboBox.setCurrentIndex(index)

    def loadPortfolioData(self):
        portfolioNameList = self.portfolio.list()
        portfolioNameList.sort()
        self.beerNameComboBox.clear()
        self.currentMeasurementPortfolioCombobox.clear()
        for key in portfolioNameList:
            self.beerNameComboBox.addItem(key)
            self.currentMeasurementPortfolioCombobox.addItem(key)
        self.updatePortfolioInfo_Callback()

    def loadBJCPData(self):
        self.BJCPData = recfromcsv(resourcePath('bjcp2008.csv'), delimiter=',')
        for BJCPStyle in self.BJCPData.style:
            self.BJCPStyleComboBox.addItem(BJCPStyle)
         
    def loadHistoryData(self):      
        tabledata = self.history.toList()   
        self.tablemodel = BeeralyzerTableModel(tabledata)
        self.historyTableView.setModel(self.tablemodel)
        self.historyTableView.setShowGrid(True)

        font = QFont(self.historTableFontFamily, self.historTableFontSize)
        self.displayHistoryTableFont(font.family(), font.pointSize())
        self.historyTableView.setFont(font)
        vh = self.historyTableView.verticalHeader()
        vh.setVisible(True)
        hh = self.historyTableView.horizontalHeader()
        hh.setStretchLastSection(True)
        self.historyTableView.setSortingEnabled(True)   
        self.historyTableView.resizeColumnsToContents()

    def connectActions(self):
        self.serialPortCombo.editTextChanged.connect(self.portChanged_Callback)
        self.connectPushButton.pressed.connect(self.connectPressed_Callback)
        self.connectPushButton.clicked.connect(self.connectClicked_Callback)

        self.calibratePushButton.pressed.connect(self.calibratePressed_Callback)
        self.calibratePushButton.clicked.connect(self.calibrateClicked_Callback)
        self.measurePushButton.clicked.connect(self.measureClicked_Callback)
        self.measurePushButton.pressed.connect(self.measurePressed_Callback)

        self.reloadSerialPortListButton.clicked.connect(self.reloadSerialPortListClicked_Callback)
        
        self.editPortfolioItemPushButton.clicked.connect(self.editPortfolioItemClicked_Callback)
        self.deletePortfolioItemPushButton.clicked.connect(self.deletePortfolioItemClicked_Callback)
        
        self.beerNameComboBox.currentIndexChanged.connect(self.updatePortfolioInfo_Callback)
        self.currentMeasurementPortfolioCombobox.currentIndexChanged.connect(self.updateSelectedMeasurementPortfolioInfo_Callback)
        self.currentMeasurementPortfolioCombobox.currentIndexChanged.connect(self.displayMeasurements)

        self.BJCPStyleComboBox.currentIndexChanged.connect(self.updateSelectedBJCPStyle_Callback)
        
        self.savePortfolioItemActionPushButton.clicked.connect(self.savePortfolioItemAction_Clicked)
        self.cancelPortfolioItemActionPushButton.clicked.connect(self.cancelPortfolioItemAction_Clicked)
        self.addPortfolioItemPushButton.clicked.connect(self.addPortfolioItem_Clicked)
        self.actionAbout.triggered.connect(self.about_Callback)
        self.notesToolButton.clicked.connect(self.notes_Callback)
        
        self.saveMeasurementPushButton.clicked.connect(self.saveMeasurement_Callback)
        self.exportPushButton.clicked.connect(self.exportToCSV_Callback)
        self.deletePushButton.clicked.connect(self.deleteSelectedHistoryRows_Callback)
        self.erasePushButton.clicked.connect(self.eraseAllHistoryRows_Callback)
        
        self.fontButton.clicked.connect(self.changeFont_Callback)
        
        self.serialPortCombo.editTextChanged.connect(self.configWidgetChanged_Callback)
        self.significantDigitsSpinBox.valueChanged.connect(self.configWidgetChanged_Callback)
        self.fontLineEdit.textChanged.connect(self.configWidgetChanged_Callback)
        self.defaultColorUnitsCombobox.currentIndexChanged.connect(self.configWidgetChanged_Callback)
        self.defaultTurbidityUnitsCombobox.currentIndexChanged.connect(self.configWidgetChanged_Callback)
        self.confirmOnExitCheckbox.stateChanged.connect(self.configWidgetChanged_Callback)
        self.confirmOnRecalibrateCheckbox.stateChanged.connect(self.configWidgetChanged_Callback)
        self.confirmOnHistoryDeleteCheckbox.stateChanged.connect(self.configWidgetChanged_Callback)
        self.autoConnectCheckbox.stateChanged.connect(self.configWidgetChanged_Callback)
        
        self.colorMeasurementUnitCombobox.currentIndexChanged.connect(self.displayMeasurements)
        self.dilutionCombobox.currentIndexChanged.connect(self.displayMeasurements)
               
    def configWidgetChanged_Callback(self):
        self.saveConfigClicked_Callback()
            
    def updatePortfolioInfo_Callback(self):
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
    
    def updateSelectedMeasurementPortfolioInfo_Callback(self):
        currentPortfolioName = self.currentMeasurementPortfolioCombobox.currentText()
        selectedItem = self.portfolio.get(str(currentPortfolioName))
        if selectedItem is not None:
            self.currentMinColorSpecLabel.setText(self.floatToString(selectedItem.minColor))
            self.currentMaxColorSpecLabel.setText(self.floatToString(selectedItem.maxColor))
            self.currentMinTurbiditySpecLabel.setText(self.floatToString(selectedItem.minTurbidity))
            self.currentMaxTurbiditySpecLabel.setText(self.floatToString(selectedItem.maxTurbidity))
            self.lastMeasuredDateLabel.setText(selectedItem.lastMeasurementDate)
            self.lastMeasuredValuesLabel.setText(selectedItem.lastMeasuredValues)
    
    def updateSelectedBJCPStyle_Callback(self):
        currentSelection = self.BJCPData[self.BJCPData.style==str(self.BJCPStyleComboBox.currentText())] 
        self.BJCPStyleNumberLabel.setText(str(currentSelection.number[0]))
        self.BJCPStyleMinimumColorLabel.setText(str(currentSelection.srmmin[0]))
        self.BJCPStyleMaximumColorLabel.setText(str(currentSelection.srmmax[0]))
        self.BJCPStyleMinOG.setText(str(currentSelection.ogmin[0]))
        self.BJCPStyleMaxOG.setText(str(currentSelection.ogmax[0]))
        self.BJCPStyleMinFG.setText(str(currentSelection.fgmin[0]))
        self.BJCPStyleMaxFG.setText(str(currentSelection.fgmax[0]))
        self.BJCPStyleMinABV.setText(str(currentSelection.abvmin[0]))
        self.BJCPStyleMaxABV.setText(str(currentSelection.abvmax[0]))
        self.BJCPStyleLabel.setText(str(currentSelection.category[0]))

    def reloadSerialPortListClicked_Callback(self):
        self.serialPortCombo.clear()
        self.populateSerialPortComboBox()

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
        self.dev.close()
        self.dev = None

    def getMeasurement(self):      
        
        if TEST:
            self.a430 = 0.3
            self.a700 = 0.01
            self.saveMeasurementPushButton.setEnabled(True)
            return
          
        error = False
        try:
            srmAbso = self.dev.getMeasurementBlue()[2]
            turbidityAbso = self.dev.getMeasurementGreen()[2]
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
            self.saveMeasurementPushButton.setEnabled(True)

    def updateWidgetEnabled(self):
        
        if TEST:
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
        if self.isCalibrated and self.config.confirmOnRecal:
            title = 'Please confirm'
            message = 'Beeralyzer is already calibrated. Recalibrate?'
            reply = QtGui.QMessageBox.question(self, title, message, QtGui.QMessageBox.Yes | 
                                               QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.No:
                self.updateWidgetEnabled()
                return     
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
        self.dateTimeEdit.setDateTime(QtCore.QDateTime.currentDateTime())

    def floatToString(self, floatValue):
        return '{value:1.{digits}f}'.format(value=floatValue,digits=self.significantDigitsSpinBox.value())
          
    def displayMeasurements(self):
        dilutionRatio = self.beeralyzer.getDilutionValue(self.dilutionCombobox.currentText())
        srmValue = self.beeralyzer.getSRM(self.a430, dilutionRatio)  
        self.turbidityLineEdit.setText(self.floatToString(self.a700))
        self.setColorTextColor(self.a430, self.a700)
        self.setBeerColorPreview(srmValue)
        self.setBeerColorDescription(srmValue)
        
        self.checkSpecs()
        
        self.colorLineEdit.setText(self.floatToString(srmValue))
        if self.colorMeasurementUnitCombobox.currentText() == COLOR_UNITS[0]:
            self.colorLineEdit.setText(self.floatToString(srmValue))
        elif self.colorMeasurementUnitCombobox.currentText() == COLOR_UNITS[1]:
            self.colorLineEdit.setText(self.floatToString(self.beeralyzer.getEBC(self.a430, dilutionRatio)))
        else:
            self.colorLineEdit.setText(self.floatToString(self.beeralyzer.getAbsorbance(self.a430, dilutionRatio)))
    
    def setColorTextColor(self, a430_10mm, a700_10mm):
        editor = self.colorLineEdit
        palette = editor.palette()
        if self.beeralyzer.isTurbid(a430_10mm, a700_10mm):
            palette.setColor(QtGui.QPalette.Active, QtGui.QPalette.Text, QtGui.QColor(255, 0, 0))
        else:
            palette.setColor(QtGui.QPalette.Active, QtGui.QPalette.Text, QtGui.QColor(0, 0, 0))
        editor.setPalette(palette)

    def checkSpecs(self):
        if self.currentMeasurementPortfolioCombobox.currentIndex() == -1:
            return

        #TODO: Use UNITS when checking for specs!!!
        portfolioItem = self.portfolio.get(str(self.currentMeasurementPortfolioCombobox.currentText()))
        if self.beeralyzer.isColorInRange(self.a430, str(self.dilutionCombobox.currentText()), portfolioItem.minColor, portfolioItem.maxColor):
            self.colorOOSLabel.hide()
        else:
            self.colorOOSLabel.show()
        
        #TODO: Use UNITS when checking for specs!!!
        if self.beeralyzer.isTurbidityInRange(self.a700, portfolioItem.minTurbidity, portfolioItem.maxTurbidity):
            self.turbidityOOSLabel.hide()
        else:
            self.turbidityOOSLabel.show()

    def setBeerColorPreview(self, srmValue):
        R, G, B = self.beeralyzer.getRGBfromSRM(srmValue)
        palette = self.colorPreviewEdit.palette()
        palette.setColor(QtGui.QPalette.Active, QtGui.QPalette.Base, QtGui.QColor(R, G, B))
        self.colorPreviewEdit.setPalette(palette)

    def setBeerColorDescription(self, srmValue):
        self.BJCPColorDescriptionLineEdit.setText(self.beeralyzer.getDescriptionFromSRM(srmValue))

    def saveConfigClicked_Callback(self):
        self.config.setPortName(self.serialPortCombo.currentText())
        self.config.setAutoConnect(self.autoConnectCheckbox.isChecked())
        self.config.setSignificantDigits(self.significantDigitsSpinBox.value())
        self.config.setConfirmOnExit(self.confirmOnExitCheckbox.isChecked())
        self.config.setConfirmOnDeleteHistory(self.confirmOnHistoryDeleteCheckbox.isChecked())
        self.config.setConfirmOnRecal(self.confirmOnRecalibrateCheckbox.isChecked())
        self.config.setHistoryFont(self.historTableFontFamily, self.historTableFontSize)
        self.config.setDefaultColorUnits(self.defaultColorUnitsCombobox.currentText())
        self.config.setDefaultTurbidityUnits(self.defaultTurbidityUnitsCombobox.currentText())
        self.config.save()
      
    def addPortfolioItem_Clicked(self):
        self.enterEditMode(True)
        self.beerNameComboBox.setEditable(True)
        self.beerNameComboBox.setEditText("")
    
    def editPortfolioItemClicked_Callback(self):
        self.enterEditMode(True)

    def deletePortfolioItemClicked_Callback(self):
        self.portfolio.delete(str(self.beerNameComboBox.currentText()))
        self.loadPortfolioData()
  
    def savePortfolioItemAction_Clicked(self):
        newName = str(self.beerNameComboBox.currentText())
 
        if len(self.minColorSpecLineEdit.text()) == 0:
            minColorSpec = 0.0
        else:
            minColorSpec = float(self.minColorSpecLineEdit.text())    

        if len(self.maxColorSpecLineEdit.text()) == 0:
            maxColorSpec = 0.0
        else:
            maxColorSpec = float(self.maxColorSpecLineEdit.text())
        
        if len(self.minTurbiditySpecLineEdit.text()) == 0:
            minTurbiditySpec = 0.0
        else:
            minTurbiditySpec = float(self.minTurbiditySpecLineEdit.text())

        if len(self.maxTurbiditySpecLineEdit.text()) == 0:
            maxTurbiditySpec = 0.0
        else:
            maxTurbiditySpec = float(self.maxTurbiditySpecLineEdit.text())

        self.portfolio.add(str(self.beerNameComboBox.currentText()),
                           str(self.BJCPStyleComboBox.currentText()),
                           minColorSpec,
                           maxColorSpec,
                           minTurbiditySpec,
                           maxTurbiditySpec)
        self.enterEditMode(False)
        self.loadPortfolioData()
        
        index = self.beerNameComboBox.findText(newName)
        if index != -1:
            self.beerNameComboBox.setCurrentIndex(index)    
    
    def cancelPortfolioItemAction_Clicked(self):
        self.enterEditMode(False)
        self.updatePortfolioInfo_Callback()
        
    def enterEditMode(self, enter):
        self.savePortfolioItemActionPushButton.setEnabled(enter)
        self.cancelPortfolioItemActionPushButton.setEnabled(enter)
        self.minColorLabel.setEnabled(enter)
        self.maxColorLabel.setEnabled(enter)
        self.minTurbidityLabel.setEnabled(enter)
        self.maxTurbidityLabel.setEnabled(enter)
        
        self.BJCPStyleComboBox.setEnabled(enter)
        self.addPortfolioItemPushButton.setEnabled(not enter)
        self.editPortfolioItemPushButton.setEnabled(not enter)
        self.deletePortfolioItemPushButton.setEnabled(not enter)
     
        self.minColorSpecLineEdit.setEnabled(enter)
        self.maxColorSpecLineEdit.setEnabled(enter)
        self.minTurbiditySpecLineEdit.setEnabled(enter)
        self.maxTurbiditySpecLineEdit.setEnabled(enter)

        self.tabWidget.setTabEnabled(0, not enter)
        self.tabWidget.setTabEnabled(1, not enter)
        self.tabWidget.setTabEnabled(3, not enter)

        self.beerNameComboBox.setEditable(False)
        
    def about_Callback(self):
        AboutWindow(self).exec_()

    def notes_Callback(self):
        dialog = MeasureNotes(self, self.currentNotes)
        if dialog.exec_() == QtGui.QDialog.Accepted:
            self.currentNotes = dialog.textEdit.toPlainText()
        
    def saveMeasurement_Callback(self):
        style = str(self.currentMeasurementPortfolioCombobox.currentText())
        colorUnits = str(self.colorMeasurementUnitCombobox.currentText())
        turbidityUnits = str(self.turbidityMeasurementUnitComboBox.currentText())

        try:
            color = float(self.colorLineEdit.text())          
        except ValueError:
            color = 0.0            
 
        try:
            turbidity = float(self.turbidityLineEdit.text())
        except ValueError:
            turbidity = 0.0
       
        dateTime = str(self.dateTimeEdit.dateTime().toPyDateTime().strftime("%Y-%m-%d %H:%M:%S"))
        
        record = BeeralyzerHistoryRecord()
        record.setDate(self.dateTimeEdit.date().toPyDate())
        record.setTime(self.dateTimeEdit.time().toPyTime())
        record.setOperator(str(self.operatorLineEdit.text()))
        record.setGyle(str(self.gyleLineEdit.text()))
        record.setSample(style)
        record.setDilution(str(self.dilutionCombobox.currentText()))
        record.setColorUnits(colorUnits)
        record.setTurbidityUnits(turbidityUnits)
        record.setMinColor(float(self.currentMinColorSpecLabel.text()))
        record.setMaxColor(float(self.currentMaxColorSpecLabel.text()))
        record.setMinTurbidity(float(self.currentMinTurbiditySpecLabel.text()))
        record.setMaxTurbidity(float(self.currentMaxTurbiditySpecLabel.text()))
        record.setNotes(self.currentNotes)
        
        record.setColor(color)            
        record.setTurbidity(turbidity)
              
        self.history.add(record) 
        self.tablemodel.append(record.toList())   

        self.portfolio.updateLastMeasurement(style, 
                                             color, 
                                             colorUnits, 
                                             turbidity, 
                                             turbidityUnits, 
                                             dateTime)
        
        currentPortfolioSelection = self.currentMeasurementPortfolioCombobox.currentIndex()
        self.loadPortfolioData()
        self.currentMeasurementPortfolioCombobox.setCurrentIndex(currentPortfolioSelection)

    def exportToCSV_Callback(self):
        path = QtGui.QFileDialog.getSaveFileName(self, 'Save File', '', 'CSV(*.csv)')
        self.tablemodel.exportToCSV(path)

    def deleteSelectedHistoryRows_Callback(self):
        if self.config.confirmOnDeleteHistory:
            title = 'Please confirm'
            message = 'Really delete selected rows?'
            reply = QtGui.QMessageBox.question(self, title, message, QtGui.QMessageBox.Yes | 
                                               QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.No:
                return

        count = 0
        first = -1
        for modelIndex in self.historyTableView.selectionModel().selectedRows():
            if first == -1:
                first = modelIndex.row()
            count = count + 1
        deletedKeys = self.tablemodel.removeRows(first, count, self.historyTableView.selectionModel().currentIndex())
        self.history.deleteKeys(deletedKeys)
    
    def eraseAllHistoryRows_Callback(self):
        title = 'Please confirm'
        message = 'Really delete ALL rows? This CANNOT BE UNDONE!'
        reply = QtGui.QMessageBox.warning(self, title, message, QtGui.QMessageBox.Yes | 
                                          QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            deletedKeys = self.tablemodel.removeAllRows()
            self.history.deleteKeys(deletedKeys)
    
    def changeFont_Callback(self):
        dialog = QFontDialog()
        title = "Please select font"
        newFont, ok = dialog.getFont(QFont(self.historTableFontFamily, self.historTableFontSize), self, title)

        if (ok):
            self.historTableFontFamily = newFont.family()
            self.historTableFontSize = newFont.pointSize()
            self.historyTableView.setFont(newFont)
            self.displayHistoryTableFont(newFont.family(), newFont.pointSize())
    
    def displayHistoryTableFont(self, family, size):
        self.fontLineEdit.setText(family + ", " + str(size))

    def checkForBeeralyzerDir(self):
        if not os.path.exists(BEERALYZER_DIRECTORY):
            os.mkdir(BEERALYZER_DIRECTORY)

    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myApp = BeeralyzerGui()
    sys.exit(app.exec_())
