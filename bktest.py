from backtesting import Backtest
from getstockdata import get_stock_data
from tradingrule import SmaCross
import datetime as dt
from icecream import ic

#TICKER = "PLTR" # Palantir Technologies
#TICKER = "QBTS" # D-Wave
#TICKER = "QUBT" # Quantum Computing
#TICKER = "IONQ" # IonQ
TICKER = "INTC" # Intel Corp
#TICKER = "NXE"  # NexGen Energy

df = get_stock_data(TICKER)
data = df[dt.datetime(2024,1,1):]

bt = Backtest(data, SmaCross, trade_on_close=True)

# Run backtest
result = bt.run()

# Result
print(result)

ic(bt)
# show the graph
#bt.plot(show_legend=False)







    
