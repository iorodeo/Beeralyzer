'''
Created on Nov 9, 2013

@author: jftheoret
'''

import shelve
from constants import HISTORY_DATABASE_NAME

class HistoryFile(object):

    def __init__(self):
        self.history = {}
        database = shelve.open(HISTORY_DATABASE_NAME)
        for key in database.keys():
            self.history[key] = database[key]
        database.close()

    def add(self, record):
        key = record.getKey()
        self.history[key] = record
        
        database = shelve.open(HISTORY_DATABASE_NAME)
        database[key] = record
        database.close()
        
    def toList(self):
        result = []
        
        for key in self.history:
            row = self.history[key].toList()
            result.append(row)
        
        return result
        