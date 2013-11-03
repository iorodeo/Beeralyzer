'''
Created on Nov 3, 2013

@author: jftheoret
'''
from portfolio_item import BeerPortfolioItem
from constants import PORTFOLIO_DATABASE_NAME
import shelve

class BeerPortfolio(object):
    def __init__(self):
        self.portfolio = {}
        database = shelve.open(PORTFOLIO_DATABASE_NAME)
        for key in database.keys():
            self.portfolio[key] = database[key]
        database.close()

    def add(self, name, style, minColor, maxColor, minTurbidity, maxTurbidity):
        item = BeerPortfolioItem(name, style, minColor, maxColor, minTurbidity, maxTurbidity)
        self.portfolio[name] = item
        
        database = shelve.open(PORTFOLIO_DATABASE_NAME)
        database[name] = item
        database.close()
    
    def delete(self, name):
        database = shelve.open(PORTFOLIO_DATABASE_NAME)
        del database[name]
        database.close()
    
    def list(self):
        return self.portfolio.keys()
       
    def get(self, key):
        item = self.portfolio.get(key)
        return item