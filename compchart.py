import plotly.graph_objs as go
import datetime as dt
import pandas as pd
import talib as ta
import numpy as np
from getstockdata import getPriceHistory,get_stock_data
from icecream import ic

#TICKER = "PLTR" # Palantir Technologies
#TICKER = "QBTS" # D-Wave
#TICKER = "QUBT" # Quantum Computing
#TICKER = "IONQ" # IonQ
#TICKER = "INTC" # Intel Corp
TICKER = "NXE"  # NexGen Energy

NAME = ""
st = dt.datetime(2020,1,1)
ed = dt.datetime.today()

df = get_stock_data(TICKER)
df.set_index('Date', inplace=True)

df['Date'] = df.index.strftime('%m-%d-%Y')
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

rdf = df[dt.datetime(2024,1,1):]

layout = {

    'title' : {"text" : "{}  {}".format(TICKER, NAME), "x":0.5},
    "xaxis" : {"title" : "日付", "rangeslider": {"visible": False} },
    "yaxis" : {"title" : "価格", "side": "left", "tickformat": "," },
    "plot_bgcolor": "light blue"
    }

data = [
        go.Candlestick(x=rdf.Date, open=rdf["Open"], high=rdf["High"],
                       low = rdf["Low"], close=rdf["Close"],
                       increasing_line_color="red",
                       increasing_line_width=1.0,
                       increasing_fillcolor="red",
                       decreasing_line_color="gray",
                       decreasing_line_width=1.0,
                       decreasing_fillcolor="gray"),
        # 5 days average
        go.Scatter(x=rdf["Date"], y=rdf["ma5"], name="MA5",
                   line={"color": "royalblue", "width":1.2} ),
        # 25 days average
        go.Scatter(x=rdf["Date"], y=rdf["ma25"], name="MA25",
                   line={"color": "lightseagreen", "width":1.2}),

        # Golden Cross
        go.Scatter(x=rdf["Date"], y=rdf["golden"], name="Golden Cross",
                   opacity=0.5, mode="markers",
                   marker={"size":15, "color": "magenta", "symbol":"triangle-up"}),
        # Dead Cross
        go.Scatter(x=rdf["Date"], y=rdf["dead"], name="Dead Cross",
                   opacity=0.8, mode="markers",
                   marker={"size":15, "color": "black", "symbol":"triangle-down"})
        
        ]

fig = go.Figure(data = data, layout = go.Layout(layout))

fig.update_layout({
    "xaxis":{
        "tickvals": rdf.Date[::2],
        "ticktext": ["{}-{}".format(x.split("-")[0], x.split("-")[1])
                     for x in rdf.Date[::2]]
     }
 })
    
fig.show()




