'''
Created on Oct 26, 2013

@author: jftheoret
'''
import platform
import sys
import csv

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import QFont
from colorimeter.colorimeter_serial import Colorimeter
import colorimeter.constants
from numpy import recfromcsv
import numpy.random

from about_gui import AboutWindow
from beer_constants import COLOR_UNITS, DILUTION_VALUES, TURBIDITY_UNITS
from beeralyzer import Beeralyzer
from config import BeeralyzerConfigFile
from history_file import HistoryFile
from history_record import BeeralyzerHistoryRecord
from history_tablemodel import BeeralyzerTableModel
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
        
        self.history = HistoryFile()
        self.tablemodel = None
        
        self.a430 = 0.0
        self.a700 = 0.0

        self.statusbar.showMessage('Not Connected')
        
        self.populateSerialPortComboBox()
        self.loadConfiguration() 
        self.loadPortfolioData()   
        self.loadBJCPData()   
        self.populateMeasurementUnits()
        self.loadHistoryData()
            
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

    def populateMeasurementUnits(self):
        self.colorMeasurementUnitComboBox.clear()
        self.turbidityMeasurementUnitComboBox.clear()
        self.dilutionComboBox.clear()
        for value in COLOR_UNITS.itervalues():
            self.colorMeasurementUnitComboBox.addItem(value)
        for value in TURBIDITY_UNITS.itervalues():
            self.turbidityMeasurementUnitComboBox.addItem(value)
        for value in DILUTION_VALUES.itervalues():
            self.dilutionComboBox.addItem(value)

    def loadConfiguration(self):
        if self.config.load():
            self.significantDigitsSpinBox.setValue(self.config.significantDigits)
            self.autoConnectCheckBox.setChecked(self.config.autoConnect)
            self.confirmOnExitCheckbox.setChecked(self.config.confirmOnExit)
            self.confirmOnRecalibrateCheckbox.setChecked(self.config.confirmOnRecal)
            self.confirmOnHistoryDeleteCheckbox.setChecked(self.config.confirmOnDeleteHistory)
            index = self.serialPortCombo.findText(self.config.serialPortName)
            if index != -1:
                self.serialPortCombo.setCurrentIndex(index)
                if self.config.autoConnect:
                    self.connectDevice()

    def loadPortfolioData(self):
        portfolioNameList = self.portfolio.list()
        portfolioNameList.sort()
        self.beerNameComboBox.clear()
        self.currentMeasurementPortfolioComboBox.clear()
        for key in portfolioNameList:
            self.beerNameComboBox.addItem(key)
            self.currentMeasurementPortfolioComboBox.addItem(key)
        self.updatePortfolioInfo_Callback()

    def loadBJCPData(self):
        self.BJCPData = recfromcsv('bjcp2008.csv', delimiter=',')
        for BJCPStyle in self.BJCPData.style:
            self.BJCPStyleComboBox.addItem(BJCPStyle)
         
    def loadHistoryData(self):
        
        tabledata = self.history.toList()   
        self.tablemodel = BeeralyzerTableModel(tabledata)
        self.historyTableView.setModel(self.tablemodel)
        self.historyTableView.setShowGrid(True)

        font = QFont("Courier New", 10)
        self.historyTableView.setFont(font)
        vh = self.historyTableView.verticalHeader()
        vh.setVisible(True)
        hh = self.historyTableView.horizontalHeader()
        hh.setStretchLastSection(True)
        self.historyTableView.setSortingEnabled(True)   
        self.historyTableView.resizeColumnsToContents()
        
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
        currentPortfolioName = self.currentMeasurementPortfolioComboBox.currentText()
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
        self.editPortfolioItemPushButton.clicked.connect(self.editPortfolioItemClicked_Callback)
        self.deletePortfolioItemPushButton.clicked.connect(self.deletePortfolioItemClicked_Callback)
        
        self.beerNameComboBox.currentIndexChanged.connect(self.updatePortfolioInfo_Callback)
        self.currentMeasurementPortfolioComboBox.currentIndexChanged.connect(self.updateSelectedMeasurementPortfolioInfo_Callback)
        self.BJCPStyleComboBox.currentIndexChanged.connect(self.updateSelectedBJCPStyle_Callback)
        
        self.savePortfolioItemActionPushButton.clicked.connect(self.savePortfolioItemAction_Clicked)
        self.cancelPortfolioItemActionPushButton.clicked.connect(self.cancelPortfolioItemAction_Clicked)
        self.addPortfolioItemPushButton.clicked.connect(self.addPortfolioItem_Clicked)
        self.actionAbout.triggered.connect(self.about_Callback)
        
        self.saveMeasurementPushButton.clicked.connect(self.saveMeasurement)
        self.exportPushButton.clicked.connect(self.exportToCSV)
        self.deletePushButton.clicked.connect(self.deleteSelectedHistoryRows)
        
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
        if self.isCalibrated:
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
        self.dateTimeEdit.setDateTime(QtCore.QDateTime.currentDateTime())
    
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
        self.config.setConfirmOnExit(self.confirmOnExitCheckbox.isChecked())
        self.config.setConfirmOnDeleteHistory(self.confirmOnHistoryDeleteCheckbox.isChecked())
        self.config.setConfirmOnRecal(self.confirmOnRecalibrateCheckbox.isChecked())
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
        self.portfolio.add(str(self.beerNameComboBox.currentText()),
                           str(self.BJCPStyleComboBox.currentText()),
                           float(self.minColorSpecLineEdit.text()),
                           float(self.maxColorSpecLineEdit.text()),
                           float(self.minTurbiditySpecLineEdit.text()),
                           float(self.maxTurbiditySpecLineEdit.text()))
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
    
    def saveMeasurement(self):
        style = str(self.currentMeasurementPortfolioComboBox.currentText())
        colorUnits = str(self.colorMeasurementUnitComboBox.currentText())
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
        record.setDilution(str(self.dilutionComboBox.currentText()))
        record.setColorUnits(colorUnits)
        record.setTurbidityUnits(turbidityUnits)
        record.setMinColor(float(self.currentMinColorSpecLabel.text()))
        record.setMaxColor(float(self.currentMaxColorSpecLabel.text()))
        record.setMinTurbidity(float(self.currentMinTurbiditySpecLabel.text()))
        record.setMaxTurbidity(float(self.currentMaxTurbiditySpecLabel.text()))
        
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
        
        self.loadPortfolioData()

    def exportToCSV(self):
        path = QtGui.QFileDialog.getSaveFileName(self, 'Save File', '', 'CSV(*.csv)')
        if not path.isEmpty():
            with open(unicode(path), 'wb') as stream:
                writer = csv.writer(stream)
                for row in range(self.tablemodel.rowCount()):
                    rowdata = []
                    for column in range(self.tablemodel.columnCount()):
                        item = self.tablemodel.item(row, column)
                        if item is not None:
                            rowdata.append(item)
                        else:
                            rowdata.append('')
                    writer.writerow(rowdata)

    def deleteSelectedHistoryRows(self):
        count = 0
        first = -1
        for modelIndex in self.historyTableView.selectionModel().selectedRows():
            if first == -1:
                first = modelIndex.row()
            count = count + 1
        deletedKeys = self.tablemodel.removeRows(first, count, self.historyTableView.selectionModel().currentIndex())
        self.history.deleteKeys(deletedKeys)
                
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myApp = beeralyzerGui()
    sys.exit(app.exec_())