#-*- coding: utf-8 -*-

import streamlit as st
import dafinance as fi
import dash 
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import streamlit as st
from icecream import ic


class Dashboard():

    def __init__(self):
        
        self.ticker  = None
        self.analyze = None
        self.fig     = None
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.VAPOR])
        

        if 'spinning_top' not in st.session_state:
            st.session_state.spinning_top = 0

        if 'engulfing' not in st.session_state:
            st.session_state.engulfing = 0

        if 'three_outside' not in st.session_state:
            st.session_state.three_outside = 0

        if 'three_inside' not in st.session_state:
            st.session_state.three_inside = 0
            
    
    def main(self):

        # Left side bar
        with st.sidebar.container():
            option = st.selectbox(
                      "Pick one of tickers",
                ('S&P500',"PLTR", "QBTS","IONQ","PDYN", "BBAI", "INTC", "NBIS", "TSLL", "RZLV")
            )
            match option:
               case "PLTR":
                  self.ticker = "PLTR"
               case "QBTS":
                  self.ticker = "QBTS"
               case "IONQ":
                  self.ticker = "IONQ"
               case "PDYN":
                  self.ticker = "PDYN"
               case "BBAI":
                  self.ticker = "BBAI"
               case "INTC":
                  self.ticker = "INTC"
               case "NBIS":
                  self.ticker = "NBIS"
               case "TSLL":
                  self.ticker = "TSLL"
               case "S&P500":
                  self.ticker = "^GSPC"
               case "RZLV":
                  self.ticker = "RZLV"
               case _:
                  self.ticker = None

        ### Get Histrical Data 
        df = fi.StockData(self.ticker).getHistory()
        if df is not None:
            # Technical Analyze
            self.analyze =  fi.TechnicalAnalysis(df)
            # Display charts
            self.fig = self.analyze.charts(self.ticker)
        else:
            self.analyze = None

        # Side bar
        with  st.sidebar:
            # 2 columns in side bar
            col1, col2 = st.columns(2, vertical_alignment="center")

            # Spinning top
            if col1.button("Spinning top", type="primary"):
                if self.ticker is None:
                    return
                if st.session_state.spinning_top == 0:
                    self.fig.add_traces(self.analyze.draw_spinning_top())
                    st.session_state.Spinning_top = 1
                else:
                    # Redraw figures 
                    go.FigureWidget(self.fig)
                    st.session_state.Spinning_top = 0

            # Engulfing
            if col2.button("Engulfing", type="primary"):
                if self.ticker is None:
                    return
                if st.session_state.engulfing == 0:
                    self.fig.add_traces(self.analyze.draw_engulfing())
                    st.session_state.engulfing = 1
                else:
                    # Redraw figures 
                    go.FigureWidget(self.fig)
                    st.session_state.engulfing = 0

            # 3 outside
            if col1.button("3 Outside", type="primary"):
                if self.ticker is None:
                    return
                if st.session_state.three_outside == 0:
                    self.fig.add_traces(self.analyze.draw_three_outside())
                    st.session_state.three_outside = 1
                else:
                    # Redraw figures 
                    go.FigureWidget(self.fig)
                    st.session_state.three_outside = 0

            # 3 inside
            if col2.button("3 Inside", type="primary"):
                if self.ticker is None:
                    return
                if st.session_state.three_inside == 0:
                    self.fig.add_traces(self.analyze.draw_three_inside())
                    st.session_state.three_inside = 1
                else:
                    # Redraw figures 
                    go.FigureWidget(self.fig)
                    st.session_state.three_inside = 0
                    

        # Center
        with st.container():

            tab1, tab2, tab3 = st.tabs(["Charts", "Correlation", "None"])

            with tab1:
                st.header(self.ticker)

                if self.fig is not None:
                    st.plotly_chart(self.fig)

            with tab2:
                st.header("Correlation")

                option = st.selectbox(
                    "Pick one of Index",
                    ("Copper", "Semiconductor","Transportation Average","Russel2000", "VIX", "SKEW", "Gold", "Dollar index", "High Yield index", "10 years Bond")
                    )
                match option:
                    case "Copper":
                        self.ticker = "HG=F"
                    case "Semiconductor":
                        self.ticker = "SOXX"
                    case "Transportation Average":
                        self.ticker = "DJT"
                    case "Russel2000":
                        self.ticker = "^RUT"
                    case "VIX":
                        self.ticker = "VIX"
                    case "SKEW":
                        self.ticker = "^SKEW"
                    case "Gold":
                        self.ticker = "GLD"
                    case "Dollar index":
                        self.ticker = "DX-Y.NYB"
                    case "High Yield index":
                        self.ticker = "HYG"
                    case "10 Years Bond":
                        self.ticker = "^TNX"

                cor = fi.Correlation()
                fig = cor.getGraph(self.ticker)
                # fig.show()
                

            with tab3:
                st.header("None")


if __name__ == "__main__":

    app = Dashboard()
    app.main()
