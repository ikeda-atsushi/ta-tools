#!/misc/aikeda/home/aikeda/Finance/venv/bin/python

import pandas_datareader.data as pdr
import datetime as dt
import matplotlib.pyplot as plt
import mplfinance as mpf
from icecream import ic

def get_stock_date(code, start, end):
    df = pdr.DataReader(code, "stooq", start, end).sort_index()
    return df

st = dt.datetime(2015, 1, 1)
ed = dt.datetime(2024, 11, 19)

df = get_stock_date("TSM", st, ed)

# get moving average for 5 days, 25 days, 75 days
df["ma5"]  = df["Close"].rolling('5D').mean()
df["ma25"] = df["Close"].rolling('25D').mean()
df["ma75"] = df["Close"].rolling('75D').mean()

cdf = df[dt.datetime(2024, 4,1):dt.datetime(2024, 11, 19)]
adp = [mpf.make_addplot(cdf["ma5"],  label="MA5", color="blue"),
       mpf.make_addplot(cdf["ma25"], label="MA25", color="green"),
       mpf.make_addplot(cdf["ma75"], label="MA75", color="red")]

fig,axes = mpf.plot(cdf, type="candle", figratio=(2,1), addplot=adp, returnfig=True, volume=True)

mpf.show()




