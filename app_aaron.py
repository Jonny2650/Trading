import dash
import dash_core_components as dcc
import dash_html_components as html
import pickle as pkl

import datetime as dt
import pandas as pd
from pandas_datareader.data import DataReader
import plotly.plotly as py
import plotly.graph_objs as go


app = dash.Dash()
app.css.append_css({'external_url': 'https://codepen.io/aaron-moss/pen/erXjxa.css'})
app.config['suppress_callback_exceptions']=True 



#---------------------------------------------------------------------------------------------------------------------------
# Read in DATA
#---------------------------------------------------------------------------------------------------------------------------

df_table = pd.read_pickle('top_movers.pkl')
df_table = df_table.tail(25)
df_table = df_table[['symbol','close','5day_price','5day%_change']]
df_table = df_table.iloc[::-1]


df_clean_prices = pd.read_pickle('clean_prices.pkl')
ticker_list = df_clean_prices.index.levels[0].unique()
ticker_list = ticker_list.tolist()

timespan_values = [5,7,10,25,50,100,150,365,730,1095,1460]  # Values allowed in the Timespan dropdown


#---------------------------------------------------------------------------------------------------------------------------
# Generate Tables
#---------------------------------------------------------------------------------------------------------------------------

def generate_table(dataframe, max_rows=25):
    return html.Table(
        # Header

        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

#---------------------------------------------------------------------------------------------------------------------------
# Main Layout
#---------------------------------------------------------------------------------------------------------------------------

app.layout = html.Div([
    
    # Page Title
    html.Div([                   
    html.H2('Stock Explorer'),
    ],
    className='row'
    ),

    # Dropdown List of Tickers and Timespan
    html.Div(
        [
        dcc.Dropdown(
            id='stock-ticker-input',
            options=[{'label': s, 'value': s}
                    for s in ticker_list],
                     
            value=['AAPL'],
            multi=True
        ),
        html.Label('Display how many days of data?'),
        dcc.Dropdown(
            id='stock_timespan',
            options=[{'label': s, 'value': s}
                    for s in timespan_values],
            value=['25'],
            multi=False
        ),
        ],
        className='row'
    ),

    # Graphs
    html.Div(
        className="row",
        children=[
            html.Div(
                className="four columns",
                children=html.Div([
                    html.Label('TOP MOVERS'),
                    generate_table(df_table)  # Table of Top Movers
                    
            ])               
            ),
            html.Div(
                className="eight columns",
                children=html.Div([
                    dcc.Graph(id='graph1'),   # Candlestick 
                    dcc.Graph(id='graph3'),   # Volume
                    dcc.Graph(id='graph2')    # Moving Avg
       
            ])
            ),
            

        ]
    ),
])

#---------------------------------------------------------------------------------------------------------------------------
# Plot Graph 1 - CANDLESTICK
#---------------------------------------------------------------------------------------------------------------------------

@app.callback(
    dash.dependencies.Output('graph1', 'figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
     dash.dependencies.Input('stock_timespan', 'value')])
def update_graph1(tickers,stock_timespan):
       
    df = df_clean_prices.loc[tickers]
    df = df.reset_index()  

    try:
        days = int(stock_timespan[0])
    except:
        days = int(stock_timespan)

    candlestick = [{
         'x': df['date'][-days:],        
         'open': df['open'][-days:],
         'high': df['high'][-days:],
         'low': df['low'][-days:],
         'close': df['close'][-days:],
         'type': 'candlestick',
    }]

        
    return{
        'data': candlestick,
        'layout': {
            'xaxis':{'rangeslider': {'visible': False}},
            'title' : 'Candlestick'
        }
    }

#---------------------------------------------------------------------------------------------------------------------------
# Plot Graph 2 - VOLUME
#---------------------------------------------------------------------------------------------------------------------------

@app.callback(
    dash.dependencies.Output('graph2','figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
     dash.dependencies.Input('stock_timespan', 'value')])
def update_graph2(tickers,stock_timespan):
    
    df = df_clean_prices.loc[tickers]
    df = df.reset_index()  

    try:
        days = int(stock_timespan[0])
    except:
        days = int(stock_timespan)

    trace0 = go.Scatter(
        x = df['date'][-days:],
        y = df['close'][-days:],
        mode = 'lines',
        name = 'close')

    trace1 = go.Scatter(
        x = df['date'][-days:],
        y = df['EMA_200'][-days:],
        mode = 'lines',
        name = '200day')     


    trace2 = go.Scatter(
        x = df['date'][-days:],
        y = df['EMA_50'][-days:],
        mode = 'lines',
        name = '50day')   


    data = [trace0, trace1, trace2]

    return{
        'data': data,
        'layout': {
            'xaxis':{'rangeslider': {'visible': False}},
            'title' : 'Moving Averages'
        }
    }

#---------------------------------------------------------------------------------------------------------------------------
# Plot Graph 3 - Moving Averages
#---------------------------------------------------------------------------------------------------------------------------

@app.callback(
    dash.dependencies.Output('graph3','figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
     dash.dependencies.Input('stock_timespan', 'value')])
def update_graph3(tickers,stock_timespan):
    
    df = df_clean_prices.loc[tickers]
    df = df.reset_index()  
    #mean_volume = df['volume'].mean()

    try:
        days = int(stock_timespan[0])
    except:
        days = int(stock_timespan)

    trace1 = [go.Bar(
                x = df['date'][-days:],
                y = df['volume'][-days:]
        )]


    return{
        'data': trace1,
        'layout': {
            'xaxis':{'rangeslider': {'visible': False}},
            'title' : 'Volume'
        }
    }

#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)
