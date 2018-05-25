
# coding: utf-8

# In[2]:


from sqlalchemy import create_engine
import quandl
import pandas as pd
import numpy as np
import talib as ta
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, r2_score
from datetime import datetime as dt, timedelta


# ## SQL Connection

# In[3]:


def create_connection():
    # Login details: 
    DSN_Name = 'traderDSN' ; Login_ID = 'basic' ; pwd = 'pwd1'

    # The engine does the same job as a connection and a cursor
    engine = create_engine(r'mssql+pyodbc://'+Login_ID+':'+pwd+'@'+ DSN_Name) 

    return engine 


# In[4]:


# Create engine and query 
engine = create_connection()
query = ''' 
SELECT * FROM {schema}.{table_name}
'''.format(schema='stocks', table_name='Adjusted_Fortune_500')

# Importing a Pandas Dataframe
prices = pd.read_sql(query,engine)
prices = prices.drop(columns=['index','close', 'split coefficient','dividend amount'])
prices = prices.rename(columns={'Ticker':'symbol','adjusted close':'close','Name':'name'})


# ## Format Data

# In[5]:


# Reformat column types
prices['open']  = prices['open'].astype(float)
prices['high']  = prices['high'].astype(float)
prices['low']   = prices['low'].astype(float)
prices['close'] = prices['close'].astype(float)
prices['volume']= prices['volume'].astype(float)
prices['date'] = pd.to_datetime(prices['date'])

# Create and sort indexes
prices.set_index(['name', 'symbol', 'date'], inplace=True)
prices = prices.sort_index(level=1, ascending=True)


# In[6]:


# Calculated columns
prices  = prices.copy().loc[(prices.loc[:,'open':'volume'] != 0 ).all(axis=1)] # Don't touch this (:

# Group over the symbols. 
prices_g = prices.groupby(level=['name'])

# Calculate many moving averages, of closing prices
EMA_lengths = [20, 50, 200]  
for l in EMA_lengths: 
    prices['EMA_'+str(l)] = prices_g.close.apply(lambda x: ta.EMA(x,l))   

prices['EMA_ratio'] = prices['EMA_200']/prices['EMA_50'] # Ratio of moving average
prices['RSI'] = prices_g.close.apply(lambda x: ta.RSI(x, 14))  # 14 day relative strength index

def CCI_func(x):
    xh = x.high 
    xl = x.low 
    xc = x.close 
    return ta.CCI(high=xh, low=xl, close=xc, timeperiod=5)

prices['CCI'] = prices_g.apply(CCI_func).reset_index(level=0,).drop(columns='name')    # created an extra column. 

prices['Momentum'] = prices_g.close.apply(lambda x: ta.MOM(x, 10))  # 10 day rolling momentum changed to prices_g.close

def Stoch_fast(x, index):
    xh = x.high 
    xl = x.low 
    xc = x.close 
    return ta.STOCHF(high=xh, low=xl, close=xc, fastk_period=14, fastd_period=3)[index] # Params 14, 3    

#prices['Stoch_fastk'] = prices_g.apply(Stoch_fast, 0).reset_index(level=1,).drop(columns='symbol')   # Stochastic fast indicator
#prices['Stoch_fastd'] = prices_g.apply(Stoch_fast, 1).reset_index(level=1,).drop(columns='symbol')

# def OBV_func(x):
#    xc = x.close
#     xv = x.volume
#    return ta.OBV(xc, xv) 
#prices['OBV'] = prices_g.apply(OBV_func).reset_index(level=1,).drop(columns='symbol')  # On Balance Volume


def bband_func(x, index):
    xc = x.close
    return ta.BBANDS(xc)[index]

prices['bbandupper'] = prices_g.apply(bband_func, 0).reset_index(level=0,).drop(columns='name')
prices['bbandmiddle'] = prices_g.apply(bband_func, 1).reset_index(level=0,).drop(columns='name') 
prices['bbandlower'] =  prices_g.apply(bband_func, 2).reset_index(level=0,).drop(columns='name')

# Standadises bands
prices['bbandlowerii'] =  prices['bbandlower']/prices['close']
prices['bbandupperii'] =  prices['bbandupper']/prices['close']

# Create target column
prices['5_day_target'] = prices.groupby(['name'])['close'].transform(lambda x:x.shift(-5))
prices['perc_change']=prices['5_day_target']/prices['close']


# In[7]:


# Import treasury yield data
US_yields=quandl.get("USTREASURY/YIELD", authtoken="wdLjKc5NXiuwUhFLByKm")
US_yields=US_yields[['3 MO', '6 MO', '1 YR', '2 YR', '3 YR', '5 YR', '7 YR', '10 YR', '30 YR']]
US_yields.index.rename('date', inplace=True)


# In[8]:


# Join prices and treasury data
prices.reset_index(level='date',inplace=True)
test=pd.merge(prices, US_yields, how='left', left_on='date' , right_index=True)
test.set_index('date',append=True,inplace=True)
test.sort_index(level=1, ascending=True,inplace=True)


# In[9]:


# Remove non-calculated data
merged = test.copy().loc[(test.loc[:,'open':'30 YR'] != 0 ).all(axis=1)]
merged.drop(columns=['30 YR'], inplace=True)
merged.fillna(method='pad', inplace=True)
clean_prices = merged.loc[(merged['EMA_200'].notnull() & merged['5_day_target'].notnull())]


# In[10]:


# Reorganise columns
clean_prices=clean_prices.loc[:,[
'open',
'high',
'low',
'close',
'volume',
'EMA_20',
'EMA_50',
'EMA_200',
'bbandupper',
'bbandmiddle',
'bbandlower',
'EMA_ratio',
'RSI',
'CCI',
'Momentum',
#'Stoch_fastk',
#'Stoch_fastd',
#'OBV',
'bbandlowerii',
'bbandupperii',
'3 MO',
'6 MO',
'1 YR',
'2 YR',
'3 YR',
'5 YR',
'7 YR',
'10 YR',
'5_day_target',
'perc_change']]


# ## Machine Learning

# In[11]:


# Set test size per stock
test_size = 3


# In[12]:


# Split features and target
X = clean_prices.copy().loc[:,'EMA_ratio':'10 YR'] 
y = clean_prices.copy().loc[:, ['perc_change']]


# In[13]:


# Get series of ingroup rownumbers
X['num']= X.groupby(level=1).cumcount(ascending=False)

# Use num to split train/test by date
X_train = X.loc[X.num > test_size ].drop(columns='num')
X_test =  X.loc[X.num <= test_size ].drop(columns='num')
y_train = y.loc[X.num > test_size ]
y_test =  y.loc[X.num <= test_size ]


# In[14]:


# Train machine learning
forest = RandomForestRegressor()
forest.fit(X_train,y_train)


# In[15]:


# Create test results
y_pred = forest.predict(X_test)
y_pred = pd.DataFrame({'ans': y_pred})


# In[16]:


# R-squared value
r2_score(y_test,y_pred)


# ## Making Predictions

# In[17]:


# Extract current data
predict_days=clean_prices.sort_index(level=1, ascending=True).groupby(['name']).tail(1).loc[:,'EMA_ratio':'10 YR']


# In[18]:


predict_days['5dayforecast'] = forest.predict(predict_days)


# In[19]:


result=predict_days.join(merged, lsuffix='l',how ='left')[['close','5dayforecast']]


# In[20]:


result['5day_price']=result['close']*result['5dayforecast']


# In[21]:


result['5day%_change']=(result['5dayforecast']-1)*100


# ## Grabs today's data

# In[23]:


prep = result[['close','5day_price','5day%_change']]
prep.sort_values("5day%_change",ascending=False, inplace=True)
prep.reset_index(inplace=True)
prep.set_index('name')
tdf=timedelta(days=5)
prep=prep[prep['date']>=(dt.now()-tdf)]


# ## Pickling for Dash

# In[31]:


prep.to_pickle('top_movers.pkl')
clean_prices.to_pickle('clean_prices.pkl')

