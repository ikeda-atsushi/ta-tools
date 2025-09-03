#-*- coding: utf-8 -*-

import broker 
import pandas_datareader.data as web


class NeverFinance(broker.Broker):
    def getHistory(self, symbol):

        super.writeCach(symbol)
        
        f = web.DataReader('005930', 'naver', start='2020-09-01') #, end='2019-10-09')
        return f
