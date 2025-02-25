#-*- coding: utf-8 -*-

import yfinance as yf
import pandas as pd
import talib as ta
import numpy as np
import datetime as dt
import os
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from nicegui import ui
from icecream import ic 


class StockData:

    def __init__(self, ticker):
        if ticker is not None:
            self.ticker = ticker
        else:
            self.ticker = None

    def getHistory(self):
        if self.ticker is None:
            return None
        self.filename = 'data/' + self.ticker+'.csv'
        if os.path.isfile(self.filename):
            df = pd.read_csv(self.filename)
            df.index = pd.to_datetime(df['Date'], utc=True)
            return df.tail(360)

        company = yf.Ticker(self.ticker)
        df = company.history(period='1Y')
        df.index.name = "Date"
        df['weekday'] = df.index.weekday
        df.to_csv(self.filename, encoding='utf-8')
        return df.tail(360)

class Correlation:

    DAYS = 360
    
    def __init__(self):
        self.sp500 = self.getData('^GSPC')

    def getData(self, symbol):
        sd = StockData(symbol)
        df = sd.getHistory().tail(self.DAYS)
        return df.drop(columns=['Open','High','Low','Volume', 'Dividends', 'Stock Splits'])
        
    def getGraph(self, symbol):
        df = self.getData(symbol)
        ic(df)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self.sp500.index,
                                     y=self.sp500['Close'],
                                     mode='lines',
                                     name='S&P500',
                                     yaxis='y1')

                          )
        fig.add_trace(go.Scatter(x=df.index,
                                     y=df['Close'],
                                     mode='lines',
                                     name=symbol,
                                     yaxis='y2')
                          )

        fig.update_layout(yaxis1=dict(side='left'),
                              yaxis2=dict(side='right',
                                              showgrid=False,
                                              overlaying='y'))

        fig.update_traces(selector=0, line=dict(color='blue', width=3))
        fig.update_traces(selector=1, line=dict(color='brown', width=3))

        return fig
        

class TechnicalAnalysis:

    def __init__(self, ohlc_history):
        self.df = ohlc_history
        self.start = dt.datetime(2020,1,1)
        self.end   = dt.datetime.today()
        self.df['Date'] = pd.to_datetime(self.df.index,format="mixed", dayfirst=False, utc=True).strftime('%Y-%m-%d')
        # 5 and 25 days average
        self.df['ma5']  = ta.SMA(self.df['Close'], 5)
        self.df['ma25'] = ta.SMA(self.df['Close'], 25)

        # find a cross point between 5 and 25 days ave to find a golden cross
        self.df['cross'] = self.df['ma5'] > self.df['ma25']
        self.cross_shift = self.df['cross'].shift(1)
        tmp_gc = (self.df['cross'] != self.cross_shift) & (self.df['cross'] == True)
        self.df['golden'] = [m if g == True else np.nan for g, m in zip(tmp_gc, self.df['ma5'])]
        tmp_dc = (self.df['cross'] != self.cross_shift) & (self.df['cross'] == False)
        self.df['dead'] = [m if d == True else np.nan for d, m in zip(tmp_dc, self.df['ma25'])]
        # Bollinger bands
        self.df['upper2'], _,self.df['lower2'] = ta.BBANDS(self.df["Close"], timeperiod=25, nbdevup=2, nbdevdn=2, matype=0)
        # MACD, signal, histogram
        self.df["macd"], self.df["macd_signal"], self.df["hist"] = ta.MACD(self.df["Close"], fastperiod=12,
                                                    slowperiod=26, signalperiod=9)
        # RSI
        self.df["rsi14"] = ta.RSI(self.df["Close"], timeperiod=14)
        self.df["rsi28"] = ta.RSI(self.df["Close"], timeperiod=28)

        self.df["70"], self.df["30"] = [70 for _ in self.df["Close"]], [30 for _ in self.df["Close"]]

        # Stochastics
        self.df["slowK"], self.df["slowD"] = ta.STOCH(self.df["High"], self.df["Low"], self.df["Close"], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)

        # Auxiliary line
        self.df["80"], self.df["20"] = [80 for _ in self.df["Close"]], [20 for _ in self.df["Close"]]
        self.spinning_top()

        # Englufing signal detection
        mb = ta.CDLENGULFING(self.df["Open"], self.df["High"], self.df["Low"], self.df["Close"])
        self.df["eng_signal"] = mb.replace({100:"Buy", -100:"Sell", 0:""})
        self.df["eng_marker"] = (mb/100 * self.df["High"]).abs().replace({0:np.nan})

        # 3 Outside
        mb = ta.CDL3OUTSIDE(self.df["Open"], self.df["High"], self.df["Low"], self.df["Close"])
        self.df["3out_signal"] = mb.replace({100:"Buy", -100:"Sell", 0:""})
        self.df["3out_marker"] = (mb/100 * self.df["High"]).abs().replace({0:np.nan})

        # 3 Inside
        mb = ta.CDL3INSIDE(self.df["Open"], self.df["High"], self.df["Low"], self.df["Close"])
        self.df["3in_signal"] = mb.replace({100:"Buy", -100:"Sell", 0:""})
        self.df["3in_marker"] = (mb/100 * self.df["High"]).abs().replace({0:np.nan})
            

    # Golden cross
    def golden_cross(self):
        tmp_gc = (self.df['cross'] != self.cross_shift) & (self.df['cross'] == True)
        self.df['golden'] = [m if g == True else np.nan for g, m in zip(tmp_gc, self.df['ma5'])]

    # Dead cross
    def dead_cross(self):
        tmp_dc = (self.df['cross'] != self.cross_shift) & (self.df['cross'] == False)
        self.df['dead'] = [m if d == True else np.nan for d, m in zip(tmp_dc, self.df['ma25'])]

    def draw_golden_cross(self):
        # Golden Cross
        return go.Scatter(yaxis="y1", x=self.df["Date"], y=self.df["golden"], name="Golden Cross",
                          opacity=0.5, mode="markers",marker={"size":15, "color": "green", "symbol":"triangle-up"})

    def draw_dead_cross(self):
        # Dead Cross
        return go.Scatter(yaxis="y1", x=self.df["Date"], y=self.df["dead"], name="Dead Cross",
                          opacity=0.8, mode="markers",
                          marker={"size":15, "color": "red", "symbol":"triangle-down"})


    # Bollinger bands         
    def bollinger_bands(self):
        self.df['upper2'], _, self.df['lower2'] = ta.BBANDS(self.df["Close"], timeperiod=25, nbdevup=2, nbdevdn=2, matype=0)
        

    def draw_bollinger_upper(self):
#        return go.Scatter(yaxis="y1", x=self.df["Date"], y=self.df["upper2"], name="", line={"color": "brown", "width": 0})
        return go.Scatter(yaxis="y1", x=self.df["Date"], y=self.df["upper2"], name="", line={"color": "brown", "width": 1})

    
    def draw_bollinger_lower(self):
        return go.Scatter(yaxis="y1", x=self.df["Date"], y=self.df["lower2"], name="BB", line={"color": "brown", "width": 1}, fill="tonexty", fillcolor="rgba(170,170,170,.2)")


    # MACD, signal, histogram
    def macd(self):
        self.df["macd"], self.df["macd_signal"], self.df["hist"] = ta.MACD(self.df["Close"], fastperiod=12, slowperiod=26, signalperiod=9)

    def draw_macd(self):
        return go.Scatter(yaxis="y3",x=self.df["Date"], y=self.df["macd"],
                   name="MACD", line={ "color": "magenta", "width": 1})

    def draw_macd_signal(self):
        return go.Scatter(yaxis="y3", x=self.df["Date"], y=self.df["macd_signal"], name="Signal", line={"color": "green", "width": 1})
    def draw_macd_histogram(self):
        return go.Bar(yaxis="y3",x=self.df["Date"], y=self.df["hist"],
                   name="Volume", opacity=0.7, marker_color="darkblue")

    # RSI
    def rsi(self):
        self.df["rsi14"] = ta.RSI(self.df["Close"], timeperiod=14)
        self.df["rsi28"] = ta.RSI(self.df["Close"], timeperiod=28)
        self.df["70"], self.df["30"] = [70 for _ in self.df["Close"]], [30 for _ in self.df["Close"]]

    def draw_rsi14(self):
        return go.Scatter(yaxis="y4", x=self.df["Date"], y=self.df["rsi14"],
                   name="RSI14" ,line={ "color": "magenta", "width": 1})

    def draw_rsi28(self):
        return go.Scatter(yaxis="y4", x=self.df["Date"], y=self.df["rsi28"],
                   name="RSI28", line={"color": "green", "width": 1})

    def draw_30(self):
        return go.Scatter(yaxis="y4", x=self.df["Date"], y=self.df["30"],
                   name="30%", line={"color": "red", "width": 1})

    def draw_70(self):
        return go.Scatter(yaxis="y4", x=self.df["Date"], y=self.df["70"],
                   name="30%", line={"color": "red", "width": 1})
    

    # Stochastics
    def stochastics(self):
        self.df["slowK"], self.df["slowD"] = ta.STOCH(self.df["High"], self.df["Low"], self.df["Close"], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        # Auxiliary line
        self.df["80"], self.df["20"] = [80 for _ in self.df["Close"]], [20 for _ in self.df["Close"]]

    # Stochastics
    def draw_stochastics_slowK(self):
        return go.Scatter(yaxis="y5", x=self.df["Date"], y=self.df["slowK"],
                   name="slowK", line={"color": "magenta", "width": 1})
    def draw_stochastics_slowD(self):
        return go.Scatter(yaxis="y5", x=self.df["Date"], y=self.df["slowD"],
                   name="slowD", line={"color": "green", "width": 1})

    def draw_auxiliary20(self):
        return go.Scatter(yaxis="y5", x=self.df["Date"], y=self.df["20"], name="20",
                   line={"color": "red", "width": 0.5 })

    def draw_auxiliary80(self):
        return go.Scatter(yaxis="y5", x=self.df["Date"], y=self.df["80"], name="80",
                   line={"color": "red", "width": 0.5})

    def draw_volume(self):
        return go.Bar(yaxis="y6", x=self.df["Date"], y=self.df["Volume"], name="Volume",
                   marker={ "color": "slategray"})


    # Marubozu Spinning top
    def spinning_top(self):
        mb = ta.CDLMARUBOZU(self.df["Open"], self.df["High"], self.df["Low"], self.df["Close"])
        self.df["mb_signal"] = mb.replace({100:"Buy", -100:"Sell", 0:""})
        self.df["mb_marker"] = (mb/100 * self.df["High"]).abs().replace({0:np.nan})

    def draw_spinning_top(self):
        return go.Scatter(yaxis="y1", x=self.df["Date"], y=self.df["mb_marker"],
                          mode="markers+text", text=self.df["mb_signal"], textposition ="top center", name = "Marubozu",
                          marker = {"size": 12, "color": "yellow", "opacity": 0.6},
                          textfont = {"size": 14, "color": "grey"})
    

    # Tsutsumiashi Engulfing
    def draw_engulfing(self):
        return go.Scatter(yaxis="y1", x=self.df["Date"], y=self.df["eng_marker"],
                   mode="markers+text", text=self.df["eng_signal"],
                   textposition ="top center",
                   name = "ENGULFING",
                   marker = {"size": 12, "color": "blue", "opacity": 0.6},
                   textfont = {"size": 14, "color": "black"})

    # Candle 3 outside
    def draw_three_outside(self):
        return go.Scatter(yaxis="y1", x=self.df["Date"], y=self.df["3out_marker"], mode="markers+text", text=self.df["3out_signal"],
                   textposition ="top center",
                   name = "3 outside",
                   marker = {"size": 12, "color": "blue", "opacity": 0.6},
                   textfont = {"size": 14, "color": "black"})

    # Candle 3 inside
    def draw_three_inside(self):
        return go.Scatter(yaxis="y1", x=self.df["Date"], y=self.df["3in_marker"], mode="markers+text", text=self.df["3in_signal"],
                   textposition ="top center",
                   name = "3 inside",
                   marker = {"size": 12, "color": "blue", "opacity": 0.6},
                   textfont = {"size": 14, "color": "black"})

    
    # Draw a candle chart
    def charts(self, ticker, company=""):
        #rdf = self.df[self.start:self.end]
        rdf = self.df
        rdf.Date  = pd.to_datetime(self.df.index).strftime('%m-%d-%Y')
        
        layout = {
            "height": 600,
            "title" : { "text" : "{}  {}".format(ticker, company), "x":0.5},
            "xaxis" : { "rangeslider" : {"visible": False} },
            "yaxis1": { "title" : "Price($)", "side": "left", "tickformat": ","}
            }

        # 3 rows in center
        fig = make_subplots(rows=5, cols=1,shared_xaxes=True,
                            subplot_titles=[ticker,'MACD', 'RSI', ' Stochastics', 'Volume'], row_heights=[0.50, 0.30, 0.30, 0.30, 0.30])
        # row_heights: eacho figs height

        # Candlestics
        fig.add_trace(go.Candlestick(yaxis="y1", x=rdf["Date"],
                            open=rdf["Open"], high=rdf["High"],
                            low = rdf["Low"], close=rdf["Close"],
                            increasing_line_color="magenta",
                            increasing_line_width=1.0,
                            increasing_fillcolor="magenta",
                            decreasing_line_color="blue",
                            decreasing_line_width=1.0,
                            decreasing_fillcolor="blue") ,row=1, col=1)

        #------
        # Golden Dead cross
        fig.add_trace(self.draw_golden_cross(), row=1, col=1)
        fig.add_trace(self.draw_dead_cross(),row=1, col=1)
        fig.add_trace(go.Scatter(yaxis="y1", x=self.df["Date"], y=self.df["golden"], name="Golden Cross",  opacity=0.5), row=1, col=1)
        # Bollinger
        fig.add_trace(self.draw_bollinger_upper(), row=1, col=1)
        fig.add_trace(self.draw_bollinger_lower(), row=1, col=1)
        # MACD
        fig.add_trace(self.draw_macd(), row=2, col=1)
        fig.add_trace(self.draw_macd_signal(), row=2, col=1)
        fig.add_trace(self.draw_macd_histogram(), row=2, col=1)
        # RSI
        fig.add_trace(self.draw_rsi14(), row=3, col=1)
        fig.add_trace(self.draw_rsi28(), row=3, col=1)
        fig.add_trace(self.draw_30(), row=3, col=1)
        fig.add_trace(self.draw_70(), row=3, col=1)
        # Stochastics
        fig.add_trace(self.draw_stochastics_slowK(), row=4, col=1)
        fig.add_trace(self.draw_stochastics_slowD(), row=4, col=1)
        fig.add_trace(self.draw_auxiliary20(), row=4, col=1)
        fig.add_trace(self.draw_auxiliary80(), row=4, col=1)
        fig.add_trace(self.draw_volume(), row=5, col=1)


        #------

        fig.update_layout(autosize=True)
        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.update_layout(width=800,height=1400, margin=dict(t=50, b=10, l=15, r=15))
        # Back ground color for figures 
        fig.update_layout(paper_bgcolor='#154360',plot_bgcolor='#D6DBDF')

        return fig

    def get_financials(self, symbol):
        return yf.Ticker(symbol).info
