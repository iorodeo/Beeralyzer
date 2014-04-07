'''
Created on Nov 3, 2013

@author: jftheoret
'''
from portfolio_item import BeerPortfolioItem
from constants import PORTFOLIO_DATABASE_NAME
from constants import BEERALYZER_DIRECTORY
import os
import shelve

class BeerPortfolio(object):
    def __init__(self):
        self.portfolio = {}
        self.databaseFullPath = os.path.join(BEERALYZER_DIRECTORY,PORTFOLIO_DATABASE_NAME)
        database = shelve.open(self.databaseFullPath)
        for key in database.keys():
            self.portfolio[key] = database[key]
        database.close()

    def add(self, name, style, minColor, maxColor, minTurbidity, maxTurbidity):
        item = BeerPortfolioItem(name, style, minColor, maxColor, minTurbidity, maxTurbidity)
        self.portfolio[name] = item
        database = shelve.open(self.databaseFullPath)
        database[name] = item
        database.close()
    
    def delete(self, name):
        database = shelve.open(self.databaseFullPath)
        del database[name]
        database.close()
        del self.portfolio[name]
    
    def list(self):
        return self.portfolio.keys()
       
    def get(self, key):
        item = self.portfolio.get(key)
        return item
    
    def updateLastMeasurement(self, name, color, colorUnits, turbidity, turbidityUnits, dateUpdated):
        database = shelve.open(self.databaseFullPath)
        item = database[name]
        item.lastMeasuredValues = str(color) + ' ' + colorUnits + ' , ' + str(turbidity) + ' ' + turbidityUnits
        item.lastMeasurementDate = dateUpdated
        database[name] = item
        database.close()
        self.portfolio[name] = item


        
