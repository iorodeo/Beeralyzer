'''
Created on Nov 9, 2013

@author: jftheoret
'''
from PyQt4.QtGui import QDialog
from PyQt4 import uic
from PyQt4 import QtGui
from constants import VERSION

class AboutWindow(QDialog):

    def __init__(self, parent):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = uic.loadUi('about.ui', self)
        self.setModal(True)
        self.connectActions()
        self.versionLabel.setText("Version " + VERSION)
        
    def connectActions(self):
        self.okPushButton.pressed.connect(self.okPressed)
    
    def okPressed(self):
        QDialog.accept(self)
        