#-*- coding: utf-8 -*-

import broker 
import dbctr
import pandas as pd
import datetime  as dt
import sqlite3
import yfinance as yf
import io
from icecream import ic


class Yahoo(broker.Broker):

    def __init__(self):
        self.sqlcmd = dbctr.SqlCom()
    
    def getHistory(self, symbol, start='2021-01-01', end=dt.datetime.today().strftime('%Y-%m-%d')):

        history = self.sqlcmd.readCach(symbol)

        if len(history) == 0:

            try:
                history = yf.download(symbol, start, end)
            except:
                print(f"Error: Can;t download data: {e}")
                
            history = history.sort_index()
            history.index = history.index.strftime('%Y-%m-%d')

            # Remove the header
            history = pd.read_csv(io.StringIO(u""+history.to_csv(header=None)), header=None)

            rows_list = []
            for row in history.iterrows():
                tmp_row = {'Date': row[1][0], 'Open': row[1][4], 'High': row[1][2], 'Low': row[1][3], 'Close': row[1][1], 'Volume': row[1][5]}
                rows_list.append(tmp_row)
                
            history = pd.DataFrame(rows_list)

            self.sqlcmd.insertHistory(symbol, history)

            return history
        
        last_of_df = len(history) - 1
        if last_of_df > 0:
            last_day_str = history.loc[history.index[last_of_df]]['Date']
            last_day = dt.datetime.strptime(last_day_str, '%Y-%m-%d')
         
        date_today = dt.datetime.today()

        if date_today == last_day:
            return history

        # Update Cach 
        try:
            df = yf.download(symbol, last_day, date_today)
            df = df.sort_index()
            df.index = df.index.strftime('%Y-%m-%d')
            # Remove the header
            df = pd.read_csv(io.StringIO(u""+df.to_csv(header=None)), header=None)
            self.sqlcmd.insertHistory(symbol, df)
        except sqlite3.Error as e:
            print(f"Error Update Cach: {e}")
            cls.db.rollback()

        history = self.sqlcmd.readCach(symbol)

        return history

    
    def close(self):
        self.sqlcmd.close()
