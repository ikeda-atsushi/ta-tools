#-*- coding: utf-8 -*-

import pandas as pd
import yfinance as yf
from yfinance import EquityQuery
import dafinance as fi
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import sqlite3
import os
import dbctr
from icecream import ic

DBNAME = "stock.db"

############ DaLayout
class DaLayout:

    def __init__(self, app):
        self.app = app
        self.df = None
        self.fig = None 
        self.analyze = None
        self.ticker = None
        return

    def setConn(self, conn):
        self.conn = conn

    def layout(self):
        # Create layout with tabs
        layout = html.Div([
            dcc.Tabs(id="tabs-stock", value="home", className="custom-tabs",
                         children=[
                             dcc.Tab(label="Home", value="home",
                                         className="custom-tab",
                                         selected_className="custom-tab-selected",
                                         id="tab1-content"),
                             dcc.Tab(label="Register", value="register",
                                         className="custom-tab",
                                         selected_className="custom-tab-selected",
                                         id="tab2-content"),
                             dcc.Tab(label="Screen", value="screen",
                                         className="custom-tab",
                                         selected_className="custom-tab-selected",
                                         id="tab3-content"),
                             dcc.Tab(label="Info", value="info",
                                         className="custom-tab",
                                         selected_className="custom-tab-selected",
                                         id="tab4-content"),
                             dcc.Tab(label="Correlation", value="correlation",
                                         className="custom-tab",
                                         selected_className="custom-tab-selected",
                                         id="tab5-content"),
                             dcc.Tab(label="Volatility", value="volatility",
                                         className="custom-tab",
                                         selected_className="custom-tab-selected",
                                         id="tab6-content"),
            
            ]),
        html.Div(id="tabs-content",className="center"),
        ])

        return layout

    def register_callback(self):
        # Tab
        @self.app.callback(
            Output('tabs-content', 'children'),
            Input("tabs-stock", "value")
            )
        def render_tab_content(tab):
            if tab == "home":
                options = [{'label': 'S&P 500','value':"^GSPC"},
                           {'label': 'Dow Jorns','value':"^DJI"},
                           {'label': 'e.l.f beauty inc.', 'value':'ELF'},
                           {'label': 'Rocket Lab Corp.', 'value':'RKLB'},
                           {'label': 'Boardcom Inc.', 'value':'AVGO'},
                           {'label': 'SiriusPointLtd.', 'value':'SPNT'},
                           {'label': 'Rezolve AI Limited', 'value':'RZLV'},
                           {'label': 'Palantir Technologies Inc.', 'value':'PLTR'},
                           {'label': 'D-Wave Quantum Inc.', 'value':'QBTS'},
                           {'label': 'Quantum Computing Inc.', 'value':'QUBT'},
                           {'label': 'IonQ Inc.', 'value':'IONQ'},
                           {'label': 'Nebius Group', 'value':'NBIS'}]

                sidebar = html.Div(
                    id = "sidebar1",
                    className="sidebar",
                    children =
                    [   dcc.Dropdown(
                            id="dropdown1",
                            options=options,
                            value=options[0]["value"],
                            className="dropdown-menu"
                            ),
                            
                        dcc.RadioItems(
                            id="radioitems-signals",
                            options=[
                                {"label": "Spinning top", "value": 1},
                                {"label": "Engulfing", "value": 2},
                                {"label": "3 Outside", "value": 3},
                                {"label": "3 Inside", "value": 4},
                                {"label": "None", "value": 5}],
                                value=5,
                                inline=False
                        )
                    ]
                    ) # Sidebar

                tab_content  = html.Div([
                    sidebar,
                    dcc.Graph(id="graph1")
                ])

                return tab_content

            elif tab == 'register':
                center = html.Div([
                    html.H2("Symbol Register", style={"textAlign": "center"}),

                    html.Div([
                        dcc.Input(id="ticker-input", type="text", placeholder="Enter symbol (e.g., AAPL)", style={"width": "40%"}),
                        html.Button("Add", id="submit-button", n_clicks=0)
                        ], style={"textAlign": "center", "marginBottom": "20px"}),

                    html.Div(id="feedback", style={"textAlign": "center", "color": "green"}),

                    dash_table.DataTable(
                        id="company-table",
                        columns=[
                            {"name": "ID", "id": "id"},
                            {"name": "Symbol", "id": "symbol"},
                            {"name": "Company", "id": "company"}
                            ],
                        data=[],
                        style_table={"overflowX": "auto"},
                        style_cell={"textAlign": "left", "padding": "5px", "color":"black"},
                        style_header={"backgroundColor": "#1f77b4", "color": "white", "fontWeight": "bold"}
                        )
                    ])
                
                # Set initial dropdown value correctly to an existing key
                tab_content = html.Div([
                    center
                    ])

                return tab_content
                
            elif tab == "screen":
                predefined={
                    'aggressive_small_caps':'Aggressive small caps',
                    'day_gainers':'Day gainers',
                    'day_losers':'Day losers',
                    'growth_technology_stocks':'Growth technology stocks',
                    'most_actives':'Most actives',
                    'most_shorted_stocks':'Most shorted stocks',
                    'small_cap_gainers':'Small cap gainers',
                    'undervalued_growth_stocks':'Undervalued growth stocks',
                    'undervalued_large_caps':'Undervalued large caps',
                    'conservative_foreign_funds':'Conservative foreign funds',
                    'high_yield_bond':'High yield bond',
                    'portfolio_anchors':'Portfolio anchors',
                    'solid_large_growth_funds':'Solid large growth funds',
                    'solid_midcap_growth_funds':'Solid midcap growth funds'}

                sidebar = html.Div(
                    id = "sidebar3",
                    className="sidebar",
                    children =
                    [
                    html.H2("Predefined Screen Menu"),
                    dcc.Dropdown(
                        id='dropdown3',
                        options=[{'label': v, 'value': k} for k, v in predefined.items()],
                        value='most_actives'
                        ),
                    html.Div(
                        children=[
                        dcc.Store(id='screened-symbols-store'),
                        html.H1('Selected symbols'),
                        html.Div(id="screened-symbols-dropdown")
                    ])
                    ]
                ) # Sidebar

                # Set initial dropdown value correctly to an existing key
                tab_content = html.Div([
                    sidebar,
                    dcc.Graph(id='graph3')
                 ])

                return tab_content

            ### Company Info
            elif tab == "info":
                stock = yf.Ticker(self.ticker)
                info = stock.info
                tab_content = html.Div([ html.P(k + " : " + str(info[k])) for k in info.keys()])

                return tab_content 

            ### Correlation
            elif tab == "correlation":
                options = [{"label": "Copper", "value": "HG=F"},
                               {"label": "Semiconductor", "value": "SOXX"},
                               {"label": "Transportation Average Index", "value": "DJT"},
                               {"label": "Russel 2000", "value": "^RUT"}, # Small Cap stock
                               {"label": "Volatility Index", "value": "^VIX"},
                               {"label": "Skew", "value": "^SKEW"},
                               {"label": "Gold", "value": "GLD"},
                               {"label": "Doller Index", "value": "DX-Y.NYB"},
                               {"label": "High Yeild Index", "value": "HYG"}, # Junk Bond
                               {"label": "US 10 years Bond", "value": "^TNX"} 
                               ]

                sidebar = html.Div(
                        dcc.Dropdown(
                            id="dropdown2",
                            options=options,
                            value=options[0]["value"],
                            className="dropdown-menu"
                            ),
                            id = "sidebar2",
                            className="sidebar"
                    )

                tab_content  = html.Div([
                        sidebar,
                        dcc.Graph(id="graph2")
                    ])

                return tab_content

            ### Volatility
            elif tab == "volatility":

                # 銘柄リスト（必要に応じて追加）
                default_tickers = ["AVGO", "QBTS"]


                # Volatility category data (in English)
                data = {
                    "Annual Volatility": ["~5%", "10–15%", "20–30%", "40–60%", "80% or more"],
                    "Monthly Equivalent": ["~1.4%", "2.9–4.3%", "5.8–8.7%", "11–17%", ">20%"],
                    "Asset Type / Interpretation": [
                        "Bonds, ultra-stable ETFs",
                        "Index funds (e.g., S&P 500)",
                        "Growth stocks, tech stocks, typical equities",
                        "High-volatility stocks, emerging markets, thematic stocks",
                        "Cryptocurrencies, disruptive innovation stocks, speculative assets"
                        ]
                    }

                # Create DataFrame for the bottom table
                volatility_df = pd.DataFrame(data)

                # アプリレイアウト
                tab_content = html.Div([
                        html.H2("月率ボラティリティ可視化ツール", style={"textAlign": "center"}),

                        html.Label("対象銘柄をカンマで入力（例: AAPL, MSFT, TSLA）:"),
                        dcc.Input(id="ticker-input", value=",".join(default_tickers), type="text", style={'width': '100%'}),
    
                        html.Label("期間指定:"),
                        dcc.DatePickerRange(
                            id="date-picker",
                            start_date="2024-01-01",
                            end_date="2025-08-08"
                            ),

                        html.Br(), html.Br(),
                        # Insert a histom graph here
                        dcc.Graph(id="volatility-graph"),
                        html.Br(), html.Br(),
                        
                        dash_table.DataTable(
                            columns=[{"name": col, "id": col} for col in volatility_df.columns],
                            data=volatility_df.to_dict("records"),
                            style_table={
                                "overflowX": "auto"
                                },
                                style_cell={
                                    "textAlign": "left",
                                    "color": "#333333",           # 全セルのフォント色
                                    "backgroundColor": "#b6cade"  # ← セルの背景色
                                    },
                                    style_header={
                                        "backgroundColor": "#1f77b4",  # ← ヘッダーの背景色
                                        "color": "Black",
                                        "fontWeight": "bold"
                                        },
                                        style_data={
                                            "color": "#000080",            # データ部のフォント色
                                            "backgroundColor": "#f0f8ff"  # ← データ部分の背景色
                                            }
                        )
                    ])

                
                return tab_content
            
        ### Dropdown Home
        @self.app.callback(
            Output("graph1", "figure"),
            [Input("dropdown1", "value")])
        def update_graph1(symbol):
            if symbol is None:
                return None
            self.ticker = symbol
            
            ### Get Histrical Data
            df = fi.StockData().getHistory(symbol)
            # Technical Analyze
            self.analyze =  fi.TechnicalAnalysis(df)
            self.fig =  self.analyze.charts(symbol)
            return self.fig

        # Radio button
        @self.app.callback(
            Output("graph1", "figure", allow_duplicate=True),
            Input("radioitems-signals", "value"),
            prevent_initial_call=True)
        def add_trend_signal(signal):
            if signal == 1:
                return self.fig.add_traces(self.analyze.draw_spinning_top())
            elif signal == 2:
               return self.fig.add_traces(self.analyze.draw_engulfing())
            elif signal == 3:
               return self.fig.add_traces(self.analyze.draw_three_outside())
            elif signal == 4:
               return self.fig.add_traces(self.analyze.draw_three_inside())
            elif signal == 5:
               self.fig =  self.analyze.charts(self.ticker)
               return self.fig

        # Dropdown Correlation
        @self.app.callback(
            Output("graph2", "figure"),
            [Input("dropdown2", "value")])
        def update_graph2(symbol):
            
            cor = fi.Correlation()
            fig = cor.getGraph(symbol)
            return fig

        # Tab3 
        @self.app.callback(
            Output('screened-symbols-dropdown', 'children'),
            Input('dropdown3', 'value'),
            )
        def update_screen(symbol):
            q = yf.PREDEFINED_SCREENER_QUERIES[symbol]
            res = yf.screen(q['query'], q['sortField'], q['sortType'])

            options = [{'label': quote.get('longName', quote.get('displayName', 'Unknown')),
                            'value': quote['symbol']} for quote in res['quotes']]
            content = html.Div(
                children=[
                    #html.H1('Selected symbols'),
                    dcc.Dropdown(options=options, id="selected-symbol-dropdown")
                ])

            return content

        # update_graph3
        @self.app.callback(
            Output('graph3', 'figure'),
            Input('selected-symbol-dropdown', 'value'),
            State('screened-symbols-store', 'data')
            )
        def update_graph3(symbol, options):
            if symbol is None:
                return go.Figure()

            df = fi.StockData().getHistory(symbol)
            if df is None or df.empty:
                return go.Figure()

            analyze = fi.TechnicalAnalysis(df)
            return analyze.charts(symbol)


        # Callback for Volatility
        @self.app.callback(
            Output("volatility-graph", "figure"),
            Input("ticker-input", "value"),
            Input("date-picker", "start_date"),
            Input("date-picker", "end_date")
            )
        def update_graph4 (ticker_input, start_date, end_date):
            tickers = [t.strip().upper() for t in ticker_input.split(",")]

            analyze = fi.Volatility(tickers, start_date, end_date)

            return analyze.getGraph()

        # コールバック：追加処理とテーブル更新
        @self.app.callback(
            Output("company-table", "data"),
            Output("feedback", "children"),
            Input("submit-button", "n_clicks"),
            State("ticker-input", "value")
            )
        def update_table(n_clicks, symbol):
            
            message = None
            self.db = dbctr.DBCtr.get_instance()
            cursor = self.db.conn.cursor()
            
            if n_clicks > 0 and symbol:
                symbol = symbol.strip().upper()
                try:
                    info = yf.Ticker(symbol).info
                    name = info.get("longName") or info.get("shortName") or "N/A"
                    cursor.execute("INSERT OR IGNORE INTO symbols (symbol, company) VALUES (?, ?)", (symbol, name))
                    self.conn.commit()
                    if self.cursor.rowcount:
                        message = f"Added: {symbol} - {name}"
                    else:
                        message = f"{symbol} is already in the database."
                except Exception as e:
                        message = f"Error: Could not fetch data for {symbol}"

            df = pd.read_sql_query("SELECT * FROM symbols", self.db.conn)
            return df.to_dict("records"), message


################ Dashboard

class Dashboard():


    def __init__(self):

        db = dbctr.DBCtr(DBNAME)
        sqlcmd = dbctr.SqlCom()
        sqlcmd.createTables()

        self.app = Dash(__name__, suppress_callback_exceptions=True)
        dlayout = DaLayout(self.app)
        self.app.layout = dlayout.layout()
        dlayout.register_callback()

    def run(self):
        self.app.run(debug=True)


if __name__ == "__main__":
     Dashboard().run() 
