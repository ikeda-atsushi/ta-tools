#!bin/python
import yfinance as yf
import datetime as dt
from prophet import Prophet 
from getstockdata import getPriceHistory
import matplotlib.pyplot as plt

#TICKER = "PLTR" # Palantir Technologies
#TICKER = "QBTS" # D-Wave
#TICKER = "QUBT" # Quantum Computing
#TICKER = "IONQ" # IonQ
TICKER = "INTC" # Intel Corp
#TICKER = "NXE"  # NexGen Energy

st = dt.datetime(2020, 1, 1)
ed = dt.datetime.today()

df = getPriceHistory(TICKER, st, ed )
df["ds"] = df["Date"]
df = df.rename(columns={"Close":"y"})

prop = Prophet()
prop.fit(df)
future = prop.make_future_dataframe(periods=365)
forcast = prop.predict(future)
fig = prop.plot(forcast)
plt.show()

