# Step 1a: Import libraries needed
# talib need to download for installation
# Data manipulation libraries
import pandas as pd
import numpy as np

# Data visualisation
import plotly.graph_objs as go

# Data import library
import yfinance as yf

# Technical indicator library
import talib as ta

# Machine learning libraries
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report  # F-Score

# Step 1b: Import Market data
df = yf.download('TSLA', period = '1d', interval = '1m')
df

# Step 1c: Visualisation quick tips.
# declare figure
fig = go.Figure()

#Set up traces
fig.add_trace(go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'], name = 'market data'))

# Add titles
fig.update_layout(
    title='Tesla price',
    yaxis_title='Stock Price (USD per Shares)')

# X-Axes
fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="30m", step="minute", stepmode="backward"),
            dict(count=6, label="90m", step="minute", stepmode="backward"),
            dict(count=1, label="HTD", step="hour", stepmode="todate"),
            dict(step="all")
        ])
    )
)

# Show
fig.show()

# Step 2: Data Processing
# Step 2a: Data cleaning
df = df.drop(df[df['Volume'] == 0].index)
df

# Step 2b: Add Trading Indicator
# Add RSI(Relative Strength Index) + Visualisation
n=10
df['RSI'] = ta.RSI(np.array(df['Close'].shift(1)),timeperiod= n)
df

from plotly.subplots import make_subplots

fig = make_subplots(rows=2, cols=1, row_heights=[0.7, 0.3])

fig.add_trace(go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'], name = 'market data'),
              row=1, col=1)

fig.update_xaxes(
    rangeslider_visible=False)

fig.add_trace(go.Scatter(x=df.index,
                y=df['RSI'] , name = 'RSI', line=dict(color='royalblue', width=1.2)),
              row=2, col=1)

fig.show()

# Create a column by name, SMA and assign the SMA calculation to it
df['SMA'] = df['Close'].shift(1).rolling(window=n).mean()

# Create a column by name, Corr and assign the calculation of correlation to it
df['Corr'] = df['Close'].shift(1).rolling(window=n).corr(df['SMA'].shift(1))

# Create a column by name, SAR and assign the SAR calculation to it
df['SAR'] = ta.SAR(np.array(df['High'].shift(1)), np.array(df['Low'].shift(1)),
                   0.2, 0.2)

# Create a column by name, ADX and assign the ADX calculation to it
df['ADX'] = ta.ADX(np.array(df['High'].shift(1)), np.array(df['Low'].shift(1)),
                   np.array(df['Open']), timeperiod=n)

# Create columns high, low and close with previous minute's OHLC data
df['Prev_High'] = df['High'].shift(1)
df['Prev_Low'] = df['Low'].shift(1)
df['Prev_Close'] = df['Close'].shift(1)

df['OO']= df['Open'] - df['Open'].shift(1)
df['OC']= df['Open'] - df['Prev_Close']

df['Ret'] = (df['Open'].shift(-1)-df['Open'])/df['Open']

# Create n columns and assign
for i in range(1, n):
    df['return%i' % i] = df['Ret'].shift(i)

# Data cleaning
df.loc[df['Corr'] < -1, 'Corr'] = -1

df.loc[df['Corr'] > 1, 'Corr'] = 1

df = df.dropna()

# data architecture
t = .8

split = int(t*len(df))
split

# Define output signals
# Ignore warnings
import warnings
warnings.filterwarnings("ignore")

df['Signal'] = 0

df.loc[df['Ret'] > df['Ret'][:split].quantile(q=0.66), 'Signal'] = 1

df.loc[df['Ret'] < df['Ret'][:split].quantile(q=0.34), 'Signal'] = -1

df