
import yahoo_fin.stock_info as yf
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta
from icecream import ic

#plt.style.use('fivethirtyeight')
#plt.rcParams['figure.figsize'] = [24, 8]


# S&P500
sp500 = yf.get_data('^GSPC')
sp500 = sp500.tail(360)
sp500 = sp500.drop(columns=['open','high','low','adjclose','volume'])
#sp500_mean = sp500['close'].mean()

# Copper 
copper = yf.get_data('HG=F')
copper = copper.tail(360)
copper = copper.drop(columns=['open','high','low','adjclose','volume'])
#copper_mean = copper['close'].mean()
#copper_close = copper['close'] * (sp500_mean/copper_mean)

# SOX
sox = yf.get_data('SOXX')
sox = sox.tail(360)
sox = sox.drop(columns=['open','high','low','adjclose','volume'])


# DJTA
djt = yf.get_data('DJT')
djt = djt.tail(360)
djt = djt.drop(columns=['open','high','low','adjclose','volume'])

# Russel 2000
rut = yf.get_data('^RUT')
rut = rut.tail(360)
rut = rut.drop(columns=['open','high','low','adjclose','volume'])


fig = go.Figure().set_subplots(4, 1)

copper
fig.add_trace(
    go.Scatter(x=sp500.index, y=sp500.close, mode='lines', yaxis='y1', name='S&P500'),
    row=1, col=1
    )

fig.add_trace(
    go.Scatter(x=copper.index, y=copper.close, mode='lines',yaxis='y2',  name='Copper'),
    row=1, col=1
    )


# SOX
fig.add_trace(
    go.Scatter(x=sp500.index, y=sp500.close, mode='lines', yaxis='y1', name='S&P500'),
    row=2, col=1
    )

fig.add_trace(
    go.Scatter(x=sox.index, y=sox.close * 20, yaxis='y2', name='SOX'),
    row=2, col=1
    )

# DJTA
fig.add_trace(
    go.Scatter(x=sp500.index, y=sp500.close, yaxis='y1', name='S&P500'),
    row=3, col=1
    )

fig.add_trace(
    go.Scatter(x=djt.index, y=djt.close * 55, yaxis='y2', mode='lines',name='DJTA'),
    row=3, col=1
    )

# Russel 2000
fig.add_trace(
    go.Scatter(x=sp500.index, y=sp500.close, yaxis='y1', mode='lines', name='S&P500'),
    row=4, col=1
    )

fig.add_trace(
    go.Scatter(x=rut.index, y=rut.close*3, yaxis='y2', mode='lines', name='Russet'),
    row=4, col=1
    )


fig.update_layout(yaxis1=dict(side='left'), yaxis2=dict(side='right', showgrid=False, overlaying='y'))
fig.update


fig.update_layout(height=1100, width=500, title_text="S&P500")

fig.show()
