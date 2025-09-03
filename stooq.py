#-*- coding: utf-8 -*-

import broker 
import dbctr
import pandas_datareader.data as web
import pandas as pd
import datetime  as dt
import sqlite3
from icecream import ic

class Stooq(broker.Broker):

    def __init__(self):
        self.sqlcmd = dbctr.SqlCom()
    
    def getHistory(self, symbol, start='2021-01-01', end=dt.datetime.today().strftime('%Y-%m-%d')):

        if symbol == '^GSPC':
            sym = '^SPX'
        else:
            sym = symbol
            
        df = self.sqlcmd.readCach(sym)

        if len(df) == 0:
            df = web.DataReader(sym, 'stooq')
            df = df.sort_index()
            if sym == '^SPX':
                sym = '^GSPC'
            ic(df)
            self.sqlcmd.insertHistory(sym, df)
            return df

        last_of_df = len(df.index) - 1
        if last_of_df > 0:
            latest_record = dt.datetime.fromtimestamp(df.index[last_of_df].timestamp())
         
        date_today = dt.datetime.today()
        if date_today == latest_record:
            return df

        # Update Cach 
        try:
            if sym == '^GSPC':
                sym = '^SPX'
            df = web.DataReader(sym, 'stooq', latest_record, date_today)
            df = df.sort_index()
            if sym == '^SPX':
                sym == '^GSPC'
            self.sqlcmd.insertHistory(sym, df)
        except sqlite3.Error as e:
            print(f"Error Update Cach: {e}")
            cls.db.rollback()

        if sym == '^SPX':
            sym = '^GSPC'
        df = self.sqlcmd.readCach(sym)
        
        return df

    def close(self):
        self.sqlcmd.close()
