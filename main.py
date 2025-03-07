#-*- coding: utf-8 -*-

import dafinance as fi
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from icecream import ic

############ DaLayout
class DaLayout:

    def __init__(self, app):
        self.app = app
        self.df = None
        self.fig = None 
        self.analyze = None
        return

    def layout(self):
        # Create layout with tabs
        layout = html.Div([
            dcc.Tabs(id="tabs-graph", value="home", className="custom-tabs",
                         children=[
                             dcc.Tab(label="Home", value="home",
                                         className="custom-tab",
                                         selected_className="custom-tab-selected",
                                         id="tab1_content"),
                             dcc.Tab(label="Correlation", value="correlation",
                                         className="custom-tab",
                                         selected_className="custom-tab-selected",
                                         id="tab2_content"),
                             dcc.Tab(label="Stats", value="stats",
                                         className="custom-tab",
                                         selected_className="custom-tab-selected",
                                         id="tab3-content")
            ]),
        html.Div(id="tabs-content",className="center"),
        ])

        return layout

    def register_callback(self):
        # Tab
        @self.app.callback(
            Output('tabs-content', 'children'),
            Input("tabs-graph", "value")
            )
        def render_tab_content(tab):
            if tab == "home":
                options = [{'label':'S&P500','value':"^GSPC"},
                           {'label': 'Palantir Technologies Inc.', 'value':'PLTR'},
                           {'label': 'D-Wave Quantum Inc.', 'value':'QBTS'},
                           {'label': 'IonQ Inc.', 'value':'IONQ'},
                           {'label': 'Plladyne AI Corp.', 'value':'PDYN'},
                           {'label': 'BigBear AI Holdings', 'value':'BBAI'},
                           {'label': 'Intel Corp.', 'value':'INTC'},
                           {'label': 'Nebius Group', 'value':'NBIS'},
                           {'label': 'Direxion Shares ETF', 'value':'TSLL'},
                           {'label': 'Rezolve AI Limited', 'value':'RZLV'},
                           {'label': 'Newmont Corporation', 'value':'NEM'}]

                sidebar = html.Div(
                    id = "sidebar1",
                    className="sidebar",
                    children =
                    [   dcc.Dropdown(
                            id="dropdown_1",
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
                    ) # Div

                if self.fig is None:
                    tab = html.Div([
                        sidebar,
                        dcc.Graph(id="graph1")
                        ])
                else:
                    tab = html.Div([
                        sidebar,
                        dcc.Graph(id="graph1", figure=self.fig)                 
                        ])

                return tab
                
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
                            id="dropdown_2",
                            options=options,
                            value=options[0]["value"],
                            className="dropdown-menu"
                            ),
                            id = "sidebar2",
                            className="sidebar"
                    )

                tab = html.Div([
                        sidebar,
                        dcc.Graph(id="graph2")
                    ])

                return tab
            
            elif tab == "stats":
                return self.layout.tab3()
            
        ### Dropdown Home
        @self.app.callback(
            Output("graph1", "figure"),
            [Input("dropdown_1", "value")])
        def update_graph1(symbol):
                self.ticker = symbol
                ### Get Histrical Data
                self.df = fi.StockData(self.ticker).getHistory()
                # Technical Analyze
                self.analyze =  fi.TechnicalAnalysis(self.df)
                self.fig =  self.analyze.charts(self.ticker)
                return self.fig

        # Radio button
        @self.app.callback(
            Output("graph1", "figure", allow_duplicate=True),
            [Input("radioitems-signals", "value")],
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
            [Input("dropdown_2", "value")])
        def update_graph2(symbol):
            self.ticker = symbol
            cor = fi.Correlation()
            return cor.getGraph(self.ticker)

    
################ Dashboard

class Dashboard():

    def __init__(self):
        self.app = Dash(__name__, suppress_callback_exceptions=True)
        dlayout = DaLayout(self.app)
        self.app.layout = dlayout.layout()
        dlayout.register_callback()

    def run(self):
        self.app.run_server(debug=True)


if __name__ == "__main__":
    Dashboard().run()
