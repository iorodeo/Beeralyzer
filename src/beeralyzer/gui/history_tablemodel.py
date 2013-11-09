'''
Created on Nov 7, 2013

@author: jftheoret
'''
import operator
from PyQt4.QtCore import QAbstractTableModel 
from PyQt4.QtCore import QVariant
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from history_record import BeeralyzerHistoryRecord
from PyQt4.QtCore import QDate
from PyQt4.QtCore import QTime
from PyQt4.QtCore import QModelIndex

DATE_COLUMN   = 0
TIME_COLUMN   = 1
SAMPLE_COLUMN = 4

class BeeralyzerTableModel(QAbstractTableModel):

    def __init__(self, datain, parent=None, *args):
        """ datain: a list of lists
        """
        QAbstractTableModel.__init__(self, parent, *args) 
        self.arraydata = datain
        record = BeeralyzerHistoryRecord()
        self.headerdata = record.getDescriptions()

    def rowCount(self, parent=None): 
        return len(self.arraydata) 
 
    def columnCount(self, parent=None): 
        return len(self.headerdata) 
    
    def data(self, index, role): 

        if not index.isValid(): 
            return QVariant() 
        elif role == Qt.TextAlignmentRole and index.column() != SAMPLE_COLUMN:
            return QVariant(Qt.AlignHCenter | Qt.AlignVCenter)
        elif role != Qt.DisplayRole: 
            return QVariant() 
        
        if index.column() == DATE_COLUMN:
            return QDate(self.arraydata[index.row()][index.column()])
        elif index.column() == TIME_COLUMN:
            return QTime(self.arraydata[index.row()][index.column()])
        else:
            return QVariant(self.arraydata[index.row()][index.column()])
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))        
        if order == Qt.DescendingOrder:
            self.arraydata.reverse()
        self.emit(SIGNAL("layoutChanged()"))

    def append(self, row):
        self.arraydata.append(row)
        self.emit(SIGNAL("layoutChanged()"))
    
    def item(self, row, column):
        return self.arraydata[row][column]
    
    
    def removeRows(self, row, count, modelIndex = QModelIndex()):
        deleteFrom = row
        deleteTo = row + count - 1
        
        self.beginRemoveRows(modelIndex, deleteFrom, deleteTo)

        i = 0
        toDelete = []
        for row in self.arraydata:
            if i >= deleteFrom and i <= deleteTo:
                toDelete.append(row)
            i += 1
        
        deletedKeys = []
        for row in toDelete:
            deletedKeys.append(str(row[0]) + str(row[1]))
            self.arraydata.remove(row)
        
        self.endRemoveRows()
        self.emit(SIGNAL("layoutChanged()"))
        return deletedKeys