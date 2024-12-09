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

# df['tmp_gc'] = tmp_gc
# df['tmp_dc'] = tmp_dc
gc = [m if g == True else np.nan for g, m in zip(tmp_gc, df['ma5'])]
dc = [m if d == True else np.nan for d, m in zip(tmp_dc, df['ma25'])]
df['golden'] = gc
df['dead'] = dc

# Bollinger bands
df['upper2'], _, df['lower2'] = ta.BBANDS(df["Close"], timeperiod=25,
                              nbdevup=2, nbdevdn=2, matype=0)

rdf = df[dt.datetime(2024,1,1):]

layout = {
    "height":800,
    "title" : { "text" : "{}  {}".format(TICKER, NAME), "x":0.5},
    "xaxis" : { "title" : "Date", "rangeslider": {"visible": False} },
    "yaxis1": { "domain": [.20, 1.0], "title" : "Price($)", "side": "left", "tickformat": "," },
    "yaxis2": { "domain": [.10, .20] },
    "yaxis3": { "domain": [.00, .10], "title": "Volume", "side": "right"},
    "plot_bgcolor": "light blue"
    }

data = [
        # Candle stick
        go.Candlestick(yaxis="y1", x=rdf["Date"], open=rdf["Open"], high=rdf["High"],
                       low = rdf["Low"], close=rdf["Close"],
                       increasing_line_color="red",
                       increasing_line_width=1.0,
                       increasing_fillcolor="red",
                       decreasing_line_color="gray",
                       decreasing_line_width=1.0,
                       decreasing_fillcolor="gray"),
        # 5 days average
        go.Scatter(yaxis="y1", x=rdf["Date"], y=rdf["ma5"], name="MA5",
                   line={"color": "royalblue", "width":1.2} ),
        # 25 days average
        go.Scatter(yaxis="y1",x=rdf["Date"], y=rdf["ma25"], name="MA25",
                   line={"color": "lightseagreen", "width":1.2}),

        # Golden Cross
        go.Scatter(yaxis="y1", x=rdf["Date"], y=rdf["golden"], name="Golden Cross",
                   opacity=0.5, mode="markers",
                   marker={"size":15, "color": "magenta", "symbol":"triangle-up"}),
        # Dead Cross
        go.Scatter(yaxis="y1", x=rdf["Date"], y=rdf["dead"], name="Dead Cross",
                   opacity=0.8, mode="markers",
                   marker={"size":15, "color": "black", "symbol":"triangle-down"}),

        # Bollinger bands
        go.Scatter(yaxis="y1", x=rdf["Date"], y=rdf["upper2"], name="",
                   line={"color": "lavender", "width": 0}),
        go.Scatter(yaxis="y1", x=rdf["Date"], y=rdf["lower2"], name="",
                   line={"color": "lavender","width": 0},
                   fill="tonexty", fillcolor="rgba(170,170,170,.2)"),

        # Volume
        go.Bar(yaxis="y3", x=rdf["Date"], y=rdf["Volume"], name="Volume",
                   marker={ "color": "slategray"})
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




