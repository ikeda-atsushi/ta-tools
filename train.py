#!/misc/aikeda/home/aikeda/Finance/venv/bin/python


from getstockdata import getPriceHistory as getph
from getstockdata import getWeekNum
from datetime import datetime as dt
import numpy as np
import os
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn import linear_model
from sklearn.preprocessing import RobustScaler


TICKER="PLTR"

df = getph(TICKER, dt(2019,1,1), dt(2024,11,3))

df_shift = df.shift(-1)
df['delta_Close'] = df_shift['Close'] - df['Close']
df['Up'] = 0
for i in range(len(df)):
    if df.loc[i, 'delta_Close'] > 0:
        df.loc[i, 'Up'] = 1

df =  df.drop('delta_Close', axis=1)

# 終値の前日比
df_shift = df.shift(1)
df['Close_ratio'] = round((df['Close'] - df_shift['Close'])/df_shift['Close'], 2)

# 始値と終値の差分
df['Body'] = df['Open'] - df['Close']

# グラフの作成
#df_new = df[['Open', 'High', 'Low', 'Close', 'Close_ratio']]
#df_new.plot(kind='line')
#plt.show()

if os.path.isfile(TICKER+'.csv'):
    # Read 'tocker.csv' 
    print('Read '+TICKER+'.csv ...')
else:
    df['weeks'] = getWeekNum(df)
    list_weeks = df['weeks'].unique()
    df['days_in_week'] = 0
    for wn in list_weeks:
        df.loc[df['weeks']==wn, 'days_in_week'] = len(df.loc[df['weeks']==wn])
    df = df[['Date','weeks','days_in_week','High','Low','Open','Close', 'Close_ratio','Body','Up']]
    df.sort_values(by='Date', ascending=True, inplace=True)
    # Write to the file, 'ticker.csv'
    df.to_csv(TICKER+'.csv', index=False)

# hold 5 days in week    
df = df[df['days_in_week'] == 5]
# Remove 1 and 4 days in week
df = df[df['days_in_week'] != 4]
df = df[df['days_in_week'] != 1]


df = df[['weeks','days_in_week','High','Low','Open','Close', 'Close_ratio','Body','Up']]
scaler = RobustScaler()
scaler.fit_transform(df)

X = df[['High', 'Low', 'Open','Close', 'Close_ratio', 'Body']]
y =  df['Up']

X_train,X_test,y_train,y_test = train_test_split(X, y)

# Nuralnetwork score = -0.02
model = MLPRegressor(hidden_layer_sizes=(20,20,20,20,20,20,20,20,20,20,20,20,20),random_state=42)
model.fit(X_train, y_train)
print(model.score(X_test, y_test))

# SDG reguression socre = -4.1
#clt = linear_model.SGDRegressor()
#clt.fit(X_train, y_train)
#print(clt.score(X_test, y_test))
