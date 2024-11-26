import pandas_datareader.data as pdr
import pandas as pd
import yfinance as yf
import os
from datetime import datetime as dt

def get_stock_data_from_to_end(code, start, end):
    return pdr.DataReader(code, "stooq",start, end).sort_index()

def get_stock_data(code):
    return pdr.DataReader(code, "stooq").sort_index()

def getPriceHistory(ticker, start, end):
    if os.path.isfile(ticker+'.csv'):
        df = pd.read_csv(ticker+'.csv')
        df['Date'] = pd.to_datetime(df['Date'])
        #df = df.reset_index(drop=True)
        #df = df.drop("Volume", axis=1)
        return df
    
    df =  yf.download(ticker,start,end)
    df['weekday'] = df.index.weekday
    df['Date'] = df.index
    df = df.reset_index(drop=True)
    #df = df.drop('Volume', axis=1)
    return df

def getWeekNum(df):
    weeks=[]
    #print("Start: ", df.loc[0, "Date"] )
    #print("End: ", df.loc[len(df)-1, "Date"])

    if type(df.loc[len(df)-1,'Date']) is pd._libs.tslibs.timestamps.Timestamp:
        end = df.loc[len(df)-1,'Date']
    else:
        end = pd.to_datetime(df.loc[len(df)-1, "Date"])
        
    for i in range(len(df)):
        if type(df.loc[i,'Date']) is pd._libs.tslibs.timestamps.Timestamp:
            date = df.loc[i, "Date"]
        else:
            date = pd.to_datetime(df.loc[i, "Date"])
        weeks.append( date.isocalendar()[1] + (end.isocalendar()[0] - date.isocalendar()[0])*52)

    return weeks


