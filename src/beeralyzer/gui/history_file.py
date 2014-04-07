'''
Created on Nov 9, 2013

@author: jftheoret
'''

import os
import shelve
from constants import HISTORY_DATABASE_NAME
from constants import BEERALYZER_DIRECTORY

class HistoryFile(object):

    def __init__(self):
        self.history = {}
        self.historyFullPath = os.path.join(BEERALYZER_DIRECTORY, HISTORY_DATABASE_NAME)
        database = shelve.open(self.historyFullPath)
        for key in database.keys():
            self.history[key] = database[key]
        database.close()

    def add(self, record):
        key = record.getKey()
        self.history[key] = record
        database = shelve.open(self.historyFullPath)
        database[key] = record
        database.close()
        
    def toList(self):
        result = []
        for key in self.history:
            row = self.history[key].toList()
            result.append(row)
        return result
        
    def deleteKeys(self, keys):
        database = shelve.open(self.historyFullPath)
        for name in keys:
            del database[name]
            del self.history[name]    
        database.close()


