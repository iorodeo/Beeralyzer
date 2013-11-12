'''
Created on Nov 11, 2013

@author: jftheoret
'''

from PyQt4.QtGui import QDialog
from PyQt4 import uic
from PyQt4 import QtGui

class MeasureNotes(QDialog):

    def __init__(self, parent, text =''):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = uic.loadUi('measure_notes.ui', self)
        self.setModal(True)
        self.setWindowTitle("Enter Measure Notes")
        self.textEdit.setPlainText(text)