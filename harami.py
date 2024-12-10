import datetime as dt
import numpy as np
import talib as ta
import pandas as pd
from getstockdata import get_stock_data
import plotly.graph_objs as go
from icecream import ic

#TICKER = "PLTR" # Palantir Technologies
#TICKER = "QBTS" # D-Wave
#TICKER = "QUBT" # Quantum Computing
#TICKER = "IONQ" # IonQ
TICKER = "INTC" # Intel Corp
#TICKER = "NXE"  # NexGen Energy

NAME=""

st = dt.datetime(2020,1,1)
ed = dt.datetime.today()

# Get the market data
df = get_stock_data(TICKER)
df['Date'] = pd.to_datetime(df.index, format="mixed", dayfirst=False).strftime('%m-%d-%Y')

# Buy, Sell  signal detection
mb = ta.CDLHARAMI(df["Open"], df["High"], df["Low"], df["Close"])
df["mb_signal"] = mb.replace({100:"Buy", -100:"Sell", 0:""})
df["mb_marker"] = (mb/100 * df["High"]).abs().replace({0:np.nan})

# Get the latest 6 months data 
rdf = df[dt.datetime(2024,7,1):]

layout = {
    "title": {"text": "{} {}".format(TICKER, NAME), "x": 0.5},
    "xaxis": {"title": "Date", "rangeslider": {"visible": False}},
    "yaxis1": {"domain": [0.20, 1.0],  "title": "Price($)", "side": "left", "tickformat": ","},
    "yaxis2": {"domain": [0.10, 0.60]},
    "yaxis3": {"domain": [0.00, 0.10], "title": "Volume", "side": "right"},
    "plot_bgcolor": "light blue"

    }


data = [
        go.Candlestick(yaxis="y1", x=rdf["Date"], open=rdf["Open"], high=rdf["High"], low=rdf["Low"], close=rdf["Close"],
                       increasing_line_color="red", decreasing_line_color="gray"),

        go.Scatter(yaxis="y1", x=rdf["Date"], y=rdf["mb_marker"], mode="markers+text", text=rdf["mb_signal"],
                   textposition ="top center",
                   name = "Harami",
                   marker = {"size": 12, "color": "blue", "opacity": 0.6},
                   textfont = {"size": 14, "color": "black"}),

        go.Bar(yaxis="y3", x=rdf["Date"], y=rdf["Volume"], name="Volume", marker={ "color": "slategray"})
]

fig = go.Figure(data=data, layout=go.Layout(layout))

# Cut half data to show a clean graph
fig.update_layout({
    "xaxis":{
        "tickvals": rdf.Date[::2],
        "ticktext": ["{}-{}".format(x.split("-")[0], x.split("-")[1])
                     for x in rdf.Date[::2]]
     }
 })
    

fig.show()
          


