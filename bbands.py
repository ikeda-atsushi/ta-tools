#!/misc/aikeda/home/aikeda/Finance/venv/bin/python

import mplfinance as mpf
import datetime as dt
import talib as ta
import matplotlib.pyplot as plt
from getstockdata import get_stock_data

TICKER="INTC"

df = get_stock_data(TICKER)

close = df["Close"]

# 25 days moving average
df["ma25"] = ta.T3(df["Close"], 25)

# BBand
df["upper1"], _, df["lower1"] = ta.BBANDS(close, timeperiod=25, nbdevup=1, nbdevdn=1, matype=ta.MA_Type.T3)

df["upper2"], _, df["lower2"] = ta.BBANDS(close, timeperiod=25, nbdevup=2, nbdevdn=2, matype=ta.MA_Type.T3)

#
cdf = df[dt.datetime(2024, 4, 1):dt.datetime(2024, 11, 21)]

apd = [
       mpf.make_addplot(cdf["ma25"], label="MA25" , color="blue", width=2.0),
       mpf.make_addplot(cdf["upper1"], label="upper1", color="green", width=0.5),
       mpf.make_addplot(cdf["lower1"], label="lower1", color="green", width=0.5),
       mpf.make_addplot(cdf["upper2"], label="upper2", color="red", width=0.5),
       mpf.make_addplot(cdf["lower2"], label="lower2", color="red", width=0.5) ]


fig, axes = mpf.plot(cdf, type="candle", figratio=(2,1), addplot=apd, returnfig=True, title=TICKER)

mpf.show()
