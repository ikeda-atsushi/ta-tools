#!/misc/aikeda/home/aikeda/Finance/venv/bin/python

import mplfinance as mpf
import datetime as dt
import talib as ta
import numpy as np
import matplotlib.pyplot as plt
from getstockdata import get_stock_data, get_stock_data_from_to_end
from icecream import ic

# NXE
# INTC
# AKBA
# TSM
# NVEI
# PLTR

TICKER = "TSM"

st = dt.datetime(2019, 1, 1)
ed = dt.datetime(2024, 11, 21)

df = get_stock_data_from_to_end(TICKER, st, ed)
df["ma5"] = ta.SMA(df["Close"], 5)
df["ma25"] = ta.SMA(df["Close"], 25)
df["ma75"] = ta.SMA(df["Close"], 75)

# compair 5 days ave. and 25 ave.
df['cross'] = df['ma5'] > df['ma25']
cross_shift = df['cross'].shift(1)
# Golden cross
tmp_gc = (df['cross'] != cross_shift) & (df['cross'] == True)
# Dead cross
tmp_dc = (df['cross'] != cross_shift) & (df['cross'] == False)

df['tmp_gc'] = tmp_gc
df['tmp_dc'] = tmp_dc
gc = [m if g == True else np.nan for g, m in zip(tmp_gc, df['ma5'])]
dc = [m if d == True else np.nan for d, m in zip(tmp_dc, df['ma25'])]
df['golden'] = gc
df['dead'] = dc
ic(df)

cdf = df[dt.datetime(2024,4, 1):].copy()


apd = [mpf.make_addplot(cdf["ma5"], label="MA5", color="brown"),
       mpf.make_addplot(cdf["ma25"], label="MA25", color="blue"),
#       mpf.make_addplot(cdf["ma75"], label="MA75", color="gray"),
       mpf.make_addplot(cdf['golden'], type='scatter', markersize=120, marker='^', color='red'),
       mpf.make_addplot(cdf['dead'], type='scatter', markersize=120, marker='v', color='gray')]


fig, axes = mpf.plot(cdf, type="candle", figratio=(2,1), addplot=apd, returnfig=True, title=TICKER)

mpf.show()

