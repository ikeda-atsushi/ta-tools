#-*- coding: utf-8 -*-

import yfinance as yf
import pandas as pd
import talib as ta
import numpy as np
import datetime as dt
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from nicegui import ui
from icecream import ic
import yahoofinance
import stooq
import neverfinance
import os

SP500 = '^GSPC'


class StockData:

    def __init__(self):
        self._broker = {'Yahoo': yahoofinance.Yahoo(), 'Stooq': stooq.Stooq(), 'NeverFinance': neverfinance.NeverFinance()}
        self.broker_name = 'Yahoo'
        return

    def getHistory(self, symbol, start='2023-01-01', end=dt.datetime.today().strftime('%Y-%m-%d')):
        return  self._broker[self.broker_name].getHistory(symbol, start, end)
        
    def fileName(self, symbol):
        return 'data/' +  symbol + '.csv'

    def registerSymbol(self, symbol):


        return

    
    def write(self):
        return

class Correlation:

    def __init__(self):

        self.sp500 = self.getData(SP500)


    def getData(self, symbol):

        sd = StockData()
        df = sd.getHistory(symbol)

        return df

    def getGraph(self, symbol):

        df = self.getData(symbol)

        #######
        # Change Date to datetime
        self.sp500["Date"] = pd.to_datetime(self.sp500['Date'])
        df['Date']         = pd.to_datetime(df["Date"])
        
        # Get common date range
        start_date = max(self.sp500["Date"].min(), df["Date"].min())   # start date
        end_date   = min(self.sp500["Date"].max(), df["Date"].max())   # end date

        #ic(self.sp500[(self.sp500["Date"] >= start_date) & (self.sp500["Date"] <= end_date)].reset_index(drop=True))
        
        # Filtering 
        sp500_aligned = self.sp500[(self.sp500["Date"] >= start_date) & (self.sp500["Date"] <= end_date)].reset_index(drop=True)
        df_aligned    = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)].reset_index(drop=True)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=sp500_aligned['Date'],
                                     y=sp500_aligned['Close'],
                                     mode='lines',
                                     name='S&P 500',
                                     yaxis='y1')

                          )
        fig.add_trace(go.Scatter(x=df_aligned['Date'],
                                     y=df_aligned['Close'],
                                     mode='lines',
                                     name=symbol,
                                     yaxis='y2')
                          )

        fig.update_layout(yaxis1=dict(side='left'),
                              yaxis2=dict(side='right',
                                              showgrid=False,
                                              overlaying='y'))

        fig.update_layout(title="Correlation")
        
        fig.update_traces(selector=0, line=dict(color='blue',  width=3))
        fig.update_traces(selector=1, line=dict(color='brown', width=3))


        return fig


class Volatility:
    fig = None
    tickers = []

    def __init__(self, tickers, start_date, end_date):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        return 

    def getGraph(self):
        annual_vols = []
        
        for ticker in self.tickers:
            try:
                ############## remove yf.download !!!! ********
                df = StockData().getHistory(ticker, self.start_date, self.end_date)
                df = df[['Close']].dropna()
                df['LogReturn'] = np.log(df['Close'] / df['Close'].shift(1))
                df.dropna(inplace=True)
                daily_vol = df['LogReturn'].std()
                annual_vol = daily_vol * np.sqrt(252/12)
                annual_vols.append(round(annual_vol * 100, 2))  # %表示
            except Exception as e:
                annual_vols.append(None)

            self.fig = go.Figure(data=[
                go.Bar(
                    x=self.tickers,
                    y=annual_vols,
                    text=[f"{v}%" if v is not None else "Failed to get symbols" for v in annual_vols],
                    textposition="auto"
                        )
                ])

            self.fig.update_layout(
                title="Monthly volatility (maltiple brand)",
                yaxis_title="Volatility (%)",
                xaxis_title="Brand",
                template="plotly_white"
                )
        return self.fig

        

class TechnicalAnalysis:

    def __init__(self, df):
        if df is None:
            self.df = None
            return None
        
        self.df = df
        
        self.df.set_index('Date', inplace=True)

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
        return go.Scatter(yaxis="y1", x=self.df.index, y=self.df["golden"], name="Golden Cross",
                          opacity=0.5, mode="markers",marker={"size":15, "color": "green", "symbol":"triangle-up"})

    def draw_dead_cross(self):
        # Dead Cross
        return go.Scatter(yaxis="y1", x=self.df.index, y=self.df["dead"], name="Dead Cross",
                          opacity=0.8, mode="markers",
                          marker={"size":15, "color": "red", "symbol":"triangle-down"})


    # Bollinger bands         
    def bollinger_bands(self):
        self.df['upper2'], _, self.df['lower2'] = ta.BBANDS(self.df["Close"], timeperiod=25, nbdevup=2, nbdevdn=2, matype=0)
        

    def draw_bollinger_upper(self):
        return go.Scatter(yaxis="y1", x=self.df.index, y=self.df["upper2"], name="Bollinger upper", line={"color": "brown", "width": 1})

    
    def draw_bollinger_lower(self):
        return go.Scatter(yaxis="y1", x=self.df.index, y=self.df["lower2"], name="Bollinger lower", line={"color": "brown", "width": 1}, fill="tonexty", fillcolor="rgba(170,170,170,.2)")


    # MACD, signal, histogram
    def macd(self):
        self.df["macd"], self.df["macd_signal"], self.df["hist"] = ta.MACD(self.df["Close"], fastperiod=12, slowperiod=26, signalperiod=9)

    def draw_macd(self):
        return go.Scatter(yaxis="y3",x=self.df.index, y=self.df["macd"],
                   name="MACD", line={ "color": "magenta", "width": 1})

    def draw_macd_signal(self):
        return go.Scatter(yaxis="y3", x=self.df.index, y=self.df["macd_signal"], name="MACD Signal", line={"color": "green", "width": 1})
    def draw_macd_histogram(self):
        return go.Bar(yaxis="y3",x=self.df.index, y=self.df["hist"],
                   name="Volume", opacity=0.7, marker_color="darkblue")

    # RSI
    def rsi(self):
        self.df["rsi14"] = ta.RSI(self.df["Close"], timeperiod=14)
        self.df["rsi28"] = ta.RSI(self.df["Close"], timeperiod=28)
        self.df["70"], self.df["30"] = [70 for _ in self.df["Close"]], [30 for _ in self.df["Close"]]

    def draw_rsi14(self):
        return go.Scatter(yaxis="y4", x=self.df.index, y=self.df["rsi14"],
                   name="RSI14" ,line={ "color": "magenta", "width": 1})

    def draw_rsi28(self):
        return go.Scatter(yaxis="y4", x=self.df.index, y=self.df["rsi28"],
                   name="RSI28", line={"color": "green", "width": 1})

    def draw_30(self):
        return go.Scatter(yaxis="y4", x=self.df.index, y=self.df["30"],
                   name="30%", line={"color": "red", "width": 1})

    def draw_70(self):
        return go.Scatter(yaxis="y4", x=self.df.index, y=self.df["70"],
                   name="30%", line={"color": "red", "width": 1})
    

    # Stochastics
    def stochastics(self):
        self.df["slowK"], self.df["slowD"] = ta.STOCH(self.df["High"], self.df["Low"], self.df["Close"], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        # Auxiliary line
        self.df["80"], self.df["20"] = [80 for _ in self.df["Close"]], [20 for _ in self.df["Close"]]

    # Stochastics
    def draw_stochastics_slowK(self):
        return go.Scatter(yaxis="y5", x=self.df.index, y=self.df["slowK"],
                   name="slowK", line={"color": "magenta", "width": 1})
    def draw_stochastics_slowD(self):
        return go.Scatter(yaxis="y5", x=self.df.index, y=self.df["slowD"],
                   name="slowD", line={"color": "green", "width": 1})

    def draw_auxiliary20(self):
        return go.Scatter(yaxis="y5", x=self.df.index, y=self.df["20"], name="20",
                   line={"color": "red", "width": 0.5 })

    def draw_auxiliary80(self):
        return go.Scatter(yaxis="y5", x=self.df.index, y=self.df["80"], name="80",
                   line={"color": "red", "width": 0.5})

    def draw_volume(self):
        return go.Bar(yaxis="y6", x=self.df.index, y=self.df["Volume"], name="Volume",
                   marker={ "color": "slategray"})


    # Marubozu Spinning top
    def spinning_top(self):
        mb = ta.CDLMARUBOZU(self.df["Open"], self.df["High"], self.df["Low"], self.df["Close"])
        self.df["mb_signal"] = mb.replace({100:"Buy", -100:"Sell", 0:""})
        self.df["mb_marker"] = (mb/100 * self.df["High"]).abs().replace({0:np.nan})

    def draw_spinning_top(self):
        return go.Scatter(yaxis="y1", x=self.df.index, y=self.df["mb_marker"],
                          mode="markers+text", text=self.df["mb_signal"],
                          textposition ="top center", name = "Spinning top",
                          marker = {"size": 12, "color": "blue", "opacity": 0.6},
                          textfont = {"size": 14, "color": "grey"})
    
    # Tsutsumiashi Engulfing
    def draw_engulfing(self):
        return go.Scatter(yaxis="y1", x=self.df.index, y=self.df["eng_marker"],
                   mode="markers+text", text=self.df["eng_signal"],
                   textposition ="top center",
                   name = "Engulfing",
                   marker = {"size": 12, "color": "blue", "opacity": 0.6},
                   textfont = {"size": 14, "color": "black"})

    # Candle 3 outside
    def draw_three_outside(self):
        return go.Scatter(yaxis="y1", x=self.df.index, y=self.df["3out_marker"], mode="markers+text", text=self.df["3out_signal"],
                   textposition ="top center",
                   name = "3 outside",
                   marker = {"size": 12, "color": "blue", "opacity": 0.6},
                   textfont = {"size": 14, "color": "black"})

    # Candle 3 inside
    def draw_three_inside(self):
        return go.Scatter(yaxis="y1", x=self.df.index, y=self.df["3in_marker"], mode="markers+text", text=self.df["3in_signal"],
                   textposition ="top center",
                   name = "3 inside",
                   marker = {"size": 12, "color": "blue", "opacity": 0.6},
                   textfont = {"size": 14, "color": "black"})

    
    # Draw a candle chart
    def charts(self, ticker, company=""):
        if self.df is None:
            return None

        rdf = self.df

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
        fig.add_trace(go.Candlestick(yaxis="y1", x=rdf.index,
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
        fig.add_trace(go.Scatter(yaxis="y1", x=self.df.index, y=self.df["golden"], name="Golden Cross",  opacity=0.5), row=1, col=1)
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
        fig.update_layout(width=1100,height=1400, margin=dict(t=50, b=10, l=15, r=15))
        # Back ground color for figures 
        #fig.update_layout(paper_bgcolor='#EBEDEF',plot_bgcolor='#D6DBDF')

        fig.update_xaxes(type="category")

        return fig

    def get_financials(self, symbol):
        return yf.Ticker(symbol).info
