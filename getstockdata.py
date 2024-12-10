import pandas_datareader.data as pdr
import pandas as pd
import yfinance as yf
import os
from datetime import datetime as dt
from icecream import ic

def get_stock_data_from_to_end(ticker, start, end):
    return pdr.DataReader(ticker, "stooq",start, end).sort_index()

def get_stock_data(ticker):
    if os.path.isfile(ticker+'.csv'):
        df = pd.read_csv(ticker+'.csv')
        df.index = pd.to_datetime(df['Date'])
        return df
    
    df = pdr.DataReader(ticker, "stooq").sort_index()
    df['weekday'] = df.index.weekday
    df.to_csv(ticker+'.csv', encoding='utf-8')
    return df

def getPriceHistory(ticker, start, end):
    if os.path.isfile(ticker+'.csv'):
        df = pd.read_csv(ticker+'.csv')
        df.set_index("Date", drop=True)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    
    df =  yf.download(ticker,start,end)
    df['weekday'] = df.index.weekday
    df['Date'] = df.index
    df = df.reset_index(drop=True)
    df.to_csv(ticker+'.csv', encoding='utf-8')
    return df

def getWeekNum(df):
    weeks=[]

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


