import plotly.graph_objs as go
import datetime as dt
import pandas as pd
import talib as ta
import numpy as np
from getstockdata import getPriceHistory,get_stock_data
from icecream import ic

#TICKER = "PLTR" # Palantir Technologies
TICKER = "QBTS" # D-Wave
#TICKER = "QUBT" # Quantum Computing
#TICKER = "IONQ" # IonQ
#TICKER = "INTC" # Intel Corp
#TICKER = "NXE"  # NexGen Energy

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
# MACD, signal, histogram
df["macd"], df["macd_signal"], df["hist"] = ta.MACD(df["Close"], fastperiod=12,
                                                    slowperiod=26, signalperiod=9)
# RSI
df["rsi14"] = ta.RSI(df["Close"], timeperiod=14)
df["rsi28"] = ta.RSI(df["Close"], timeperiod=28)

df["70"], df["30"] = [70 for _ in df["Close"]], [30 for _ in df["Close"]]

# Stochastics
df["slowK"], df["slowD"] = ta.STOCH(df["High"], df["Low"], df["Close"],
                                    fastk_period=5, slowk_period=3,
                                    slowk_matype=0, slowd_period=3,
                                    slowd_matype=0)


# Auxiliary line
df["80"], df["20"] = [80 for _ in df["Close"]], [20 for _ in df["Close"]]


rdf = df[dt.datetime(2024,7,1):]

layout = {
    "height": 1000,
    "title" : { "text" : "{}  {}".format(TICKER, NAME), "x":0.5},
    "xaxis" : { "rangeslider" : {"visible": False} },
    "yaxis1": { "domain": [.46, 1.0], "title" : "Price($)", "side": "left", "tickformat": ","},
    "yaxis2": { "domain": [.40, .46] },
    # MACD
    "yaxis3": { "domain": [.30, .395], "title": "MACD", "side": "right"},
    # RSI
    "yaxis4": { "domain": [.20, .295], "title": "RSI", "side": "right"},
    # Stochastics
    "yaxis5": {"domain": [.10, .195], "title": "STC", "side": "right"},
    # Volue
    "yaxis6": {"domain": [.00, .095], "title": "Volume", "side": "right"},
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
        go.Scatter(yaxis="y1", x=rdf["Date"], y=rdf["lower2"], name="BB",
                   line={"color": "lavender","width": 0},
                   fill="tonexty", fillcolor="rgba(170,170,170,.2)"),

        # MACD
        go.Scatter(yaxis="y3",x=rdf["Date"], y=rdf["macd"],
                   name="MACD", line={ "color": "magenta", "width": 1}),
        go.Scatter(yaxis="y3", x=rdf["Date"], y=rdf["macd_signal"],
                   name="Signal", line={"color": "green", "width": 1}),
        go.Scatter(yaxis="y3",x=rdf["Date"], y=rdf["hist"],
                   name="Histgram", line={"color": "slategray"}),

        # RSI
        go.Scatter(yaxis="y4", x=rdf["Date"], y=rdf["rsi14"],
                   name="RSI14",line={"color": "magenta", "width": 1}),
        go.Scatter(yaxis="y4", x=rdf["Date"], y=rdf["rsi28"],
                   name="RSI28", line={"color": "green", "width": 1}),

        # Auxiliary line
        go.Scatter(yaxis="y4",x=rdf["Date"], y=rdf["30"], name="30",
                   line={"color": "black", "width": 0.5}),
        go.Scatter(yaxis="y4", x=rdf["Date"], y=rdf["70"], name="70",
                   line={"color": "black", "width": 0.5}),

        # Stochastics
        go.Scatter(yaxis="y5", x=rdf["Date"], y=rdf["slowK"],
                   name="slowK", line={"color": "magenta", "width": 1}),
        go.Scatter(yaxis="y5", x=rdf["Date"], y=rdf["slowD"],
                   name="slowD", line={"color": "green", "width": 1}),

        # Auxiliary line
        go.Scatter(yaxis="y5", x=rdf["Date"], y=rdf["20"], name="20",
                   line={"color": "black", "width": 0.5 }),

        go.Scatter(yaxis="y5", x=rdf["Date"], y=rdf["80"], name="80",
                   line={"color": "black", "width": 0.5}),

        # Volume
        go.Bar(yaxis="y6", x=rdf["Date"], y=rdf["Volume"], name="Volume",
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




