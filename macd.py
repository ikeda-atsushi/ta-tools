#!/misc/aikeda/home/aikeda/Finance/venv/bin/python

import mplfinance as mpf
import datetime as dt
import talib as ta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from getstockdata import get_stock_data, get_stock_data_from_to_end
from icecream import ic

# NXE
# INTC
# AKBA
# TSM
# NVEI
# PLTR

TICKER = "ARQQ"

st = dt.datetime(2019, 1, 1)
ed = dt.datetime(2024, 11, 22)

df = get_stock_data_from_to_end(TICKER, st, ed)
df["ma5"] = ta.SMA(df["Close"], 5)
df["ma25"] = ta.SMA(df["Close"], 25)


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

macd, macdsig, hist = ta.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)

df['macd'] = macd
df['macdsig'] = macdsig
df['hist'] = hist


# since Apr. 
cdf = df[dt.datetime(2024,4, 1):].copy()


#TA-Libでストキャスティクスを計算
slowk, slowd = ta.STOCH(cdf['High'], cdf['Low'], cdf['Close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
#買われすぎ、売られすぎを判断する80%と20%の基準線を作成
line_80 = pd.Series([80]*len(slowk), index=slowk.index)
line_20 = pd.Series([20]*len(slowk), index=slowk.index)

adp = [
       # 5 days ave.  blown
#       mpf.make_addplot(cdf["ma5"], panel=0, label='MA5', color='deeppink', width=0.7),
       # 25 days ave. blue
#       mpf.make_addplot(cdf["ma25"], panel=0, label='MA25', color='navy', width=0.7),
       # MACD   grey
       mpf.make_addplot(cdf["macd"], panel=1, label='MACD', color='blue',  width=0.7),
       # Signal  red
       mpf.make_addplot(cdf['macdsig'], panel=1, label='Signal', color='red', width=0.7),
       # Hist
       mpf.make_addplot(cdf['hist'], panel=2, type='bar', color='darkblue'),
       # Stochastic
       mpf.make_addplot(slowk, color='blue', width=1, panel=3, ylim=(0,100)),
       mpf.make_addplot(slowd, color='red', width=1, panel=3, ylim=(0, 100)), 
       mpf.make_addplot(line_80, linestyle='dotted', color='r', width=1, panel=3),
       mpf.make_addplot(line_20, linestyle='dotted', color='r', width=1, panel=3)
       ]

mpf.plot(cdf, type="candle", style='yahoo', figratio=(5,3), panel_ratios=(2,2,1,1), mav=(5,25), addplot=adp, title=TICKER)

mpf.show()
