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
df_table = df_table[['symbol','close','5day_price','5day%_change']]
df_table = df_table.rename(columns={'symbol':'Ticker','close':'Close','5day_price':'5 Days Predicted','5day%_change':'5 Day % Change'})
df_table['5 Days Predicted'] = df_table['5 Days Predicted'].map('{:,.2f}'.format)  # Formatting float length
df_table['Close'] = df_table['Close'].map('{:,.3f}'.format)
df_table['5 Day % Change'] = df_table['5 Day % Change'].map('{:,.2f}'.format)

df_table_top = df_table.tail(10)  # Top Movers
df_table_bot = df_table.head(10)  # Worst Movers
#print(df_table_bot)


print(df_table_top)
df_table_top = df_table_top.iloc[::-1]
print(df_table_bot)


df_clean_prices = pd.read_pickle('clean_prices.pkl')
ticker_list = df_clean_prices.index.levels[0].unique()

# df_info = df_clean_prices.reset_index()
# df_info = df_info[['symbol','name']]
# df_info = df_info.drop_duplicates()
# df_info = df_info.set_index(['symbol'])

#print(df_info.head())

ticker_list = ticker_list.tolist()

timespan_values = [5,7,10,25,50,100,150,365,730,1095,1460]  # Values allowed in the Timespan dropdown

#---------------------------------------------------------------------------------------------------------------------------
# Colour palette
#---------------------------------------------------------------------------------------------------------------------------
##
colors = {
    'FT Red'         : '#AC526E',
    'FT Light Blue'  : '#73ACBF',
    'FT Blue Grey'   : '#505B6F',
    'FT Light Grey'  : '#A6A29F',
    'FT Pink'        : '#fff1e0', 
    'FT Blue'        : '#2e6e9e',
    'FT Dark Blue'   : '#275e86',
    'FT Pink Tint 1' : '#f6e9d8',
    'FT Pink Tint 2' : '#e9decf', 
    'FT Claret'      : '#9e2f50', 
    'Oxford'         : '#0F5499',
    'Paper'          : '#FFF1E5',
    'Wheat'          : '#F2DFCE',
    'Sky'            : '#CCE6FF',
    'Slate'          : '#262A33',
    'Teal'           : '#0D7680',
    'Mandarin'       : '#FF8833',
    'Black'          : '000000',
    'White'          : 'FFFFFF',
}

#---------------------------------------------------------------------------------------------------------------------------
# Generate Tables
#---------------------------------------------------------------------------------------------------------------------------

def generate_table(dataframe, max_rows=25):
    return html.Table( 
        #style={'border': '1px solid black'}
        # Header

        [html.Tr([html.Th(col, style={'textAlign': 'center','border':'5px solid #505B6F'}) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col], style={'textAlign': 'center'}) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))], 
        style={'border':'2px solid black;'}

    )


#---------------------------------------------------------------------------------------------------------------------------
# Main Layout
#---------------------------------------------------------------------------------------------------------------------------

app.layout = html.Div(style={'backgroundColor': colors['Paper']},children=[
    
    # Page Title
    html.Div([                   
    html.H1(children='Stock Explorer',
            style={'textAlign': 'center',
                   'titlefont' : dict(
                            size=145,
                            color=colors['Slate']),
                    'backgroundcolor': colors['Paper'],
                    'color': colors['Slate']}),
    ],
    className='row'
    ),

    html.Div(
        className="row",
        children=[
            
            html.Div(
                className="one column"
            ),

            html.Div(
                className="two columns",
                children=html.Div([
                      html.Div(
                                [
                                dcc.Dropdown(
                                    id='stock-ticker-input',
                                    options=[{'label': s, 'value': s}
                                            for s in ticker_list],
                                             
                                    value=['AAPL'],
                                    multi=True
                                ),
                                html.Label(html.H4('Display how many days of data?')),
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

                   
                    html.Label(html.H2('TOP MOVERS'), style={'textAlign': 'center'}),
                    generate_table(df_table_top),  # Table of Top Movers
                    
                    html.Label(html.H2('WORST MOVERS'), style={'textAlign': 'center'}),
                    generate_table(df_table_bot)
                    
            ])               
            ),
            html.Div(
                className="seven columns",
                children=html.Div([
                    dcc.Graph(id='graph1'),   # Candlestick 
                    dcc.Graph(id='graph3'),   # Volume
                    dcc.Graph(id='graph2')    # Moving Avg
       
            ])
            ),


            html.Div(
                className="two columns",
                children=html.Div([
                    html.H2(id='stock_details', style={'textAlign': 'center'}),
                    dcc.Graph(id='pie1'),
                    dcc.Graph(id='pie2')
                    #df_info[tickers])
            ])
            ),


        ]
    ),
])

#---------------------------------------------------------------------------------------------------------------------------
# Plot Graph 1 - CANDLESTICK
#---------------------------------------------------------------------------------------------------------------------------

@app.callback(
    dash.dependencies.Output('stock_details', 'children'),
    [dash.dependencies.Input('stock-ticker-input', 'value')])

def update_stock_details(tickers):
    
    df = df_clean_prices.loc[tickers]
    df = df.reset_index()  


    name = df['name'][-1:]
    open_val = df['open'][-1:]
    high_val = df['high'][-1:]
    low_val = df['low'][-1:]
    close_val = df['close'][-1:]
    x_val = df['date'][-1:] 

    return html.Table( 
        #style={'border': '1px solid black'}
        # Header

        
        [html.Tr([html.Th([str(name.iloc[0][:-34])])])] +
        [html.Tr([html.Td(['Date: ',str(x_val.iloc[0])[:10]],style={'textAlign': 'center'})])] +
        [html.Tr([html.Td(['Open: ',str(open_val.iloc[0])],style={'textAlign': 'center'})])] +
        [html.Tr([html.Td(['High: ',str(high_val.iloc[0])],style={'textAlign': 'center'})])] +
        [html.Tr([html.Td(['Low: ',str(low_val.iloc[0])],style={'textAlign': 'center'})])] +
        [html.Tr([html.Td(['Close: ',str(close_val.iloc[0])],style={'textAlign': 'center'})])] 

    )


    #details = str(name.iloc[0][:-34]) + '  ' + str(x_val.iloc[0])[:10] +
    #'--------Open:' + str(open_val.iloc[0]) +'
    #--------High:' + str(high_val.iloc[0]) +'----
    #----Low:' + str(low_val.iloc[0]) +'--------
    #Close: ' + str(close_val.iloc[0]) 
    
    #return details 

#---------------------------------------------------------------------------------------------------------------------------
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
         'increasing' : dict(line=dict(color= colors['FT Blue'],width=5)),
         'decreasing' : dict(line=dict(color= colors['FT Claret'],width=5))

    }]

        
    return{
        'data': candlestick,
        'layout': {
            'plot_bgcolor': colors['Paper'],
            'paper_bgcolor': colors['Paper'],
            'xaxis':{'rangeslider': {'visible': False}},
            'title' : str(tickers)[2:-2] + ' - Candlestick',
            'titlefont' : dict(
                            size=25,
                            color=colors['Slate']),
            'showlegend' :False
        }
    }

#---------------------------------------------------------------------------------------------------------------------------
# Plot Graph 2 - MOVING AVG
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
        name = 'close',
        line = dict(
                color = (colors['Sky']),
                width = 7
            ))

    trace1 = go.Scatter(
        x = df['date'][-days:],
        y = df['EMA_200'][-days:],
        mode = 'lines',
        name = '200day',
        line = dict(
                color = (colors['Mandarin']),
                width = 7
            ))    


    trace2 = go.Scatter(
        x = df['date'][-days:],
        y = df['EMA_50'][-days:],
        mode = 'lines',
        name = '50day',
        line = dict(
                color = (colors['Teal']),
                width = 7
            ))   


    data = [trace0, trace1, trace2]

    return{
        'data': data,
        'layout': {
            'plot_bgcolor': colors['Paper'],
            'paper_bgcolor': colors['Paper'],
            'xaxis':{'rangeslider': {'visible': False}},
            'title' : str(tickers)[2:-2] + ' - 50 and 200 day Moving Averages',
            'titlefont' : dict(
                            size=25,
                            color=colors['Slate']),
            'legend' : dict(x=0.05, y=0.99)
        }
    }

#---------------------------------------------------------------------------------------------------------------------------
# Plot Graph 3 - VOLUME
#---------------------------------------------------------------------------------------------------------------------------

@app.callback(
    dash.dependencies.Output('graph3','figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
     dash.dependencies.Input('stock_timespan', 'value')])
def update_graph3(tickers,stock_timespan):
    df = df_clean_prices.loc[tickers]
    df = df.reset_index()  
    
    try:
        days = int(stock_timespan[0])
    except:
        days = int(stock_timespan)

    trace1 = [go.Bar(
                x = df['date'][-days:],
                y = df['volume'][-days:],
                marker=dict(
                    color = colors['Oxford'])
        )]

    return{
        'data': trace1,
        'layout': {
            'plot_bgcolor': colors['Paper'],
            'paper_bgcolor': colors['Paper'],
            'xaxis':{'rangeslider': {'visible': False}},
            'title' : str(tickers)[2:-2] + ' - Volume',
            'titlefont' : dict(
                            size=25,
                            color=colors['Slate']),
        }
    }

#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------

@app.callback(
    dash.dependencies.Output('pie1','figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value')])
def update_pie1(tickers):
    
    labels = df_table_top['Ticker'][:-5]
    values = df_table_top['5 Day % Change'][:-5]
    
    
    trace = [go.Pie(
                labels=labels, 
                values=values,
                hole='0.2',
                textinfo='none',
                textfont=dict(size=20),
                #textposition='outside',
                marker={'colors': [colors['FT Red'],
                                   colors['Oxford'],
                                   colors['Sky'],
                                   colors['Teal'],
                                   colors['Mandarin']]}

            )]
    
    return{
        'data': trace,        
        'layout': {
            'plot_bgcolor': colors['Paper'],
            'paper_bgcolor': colors['Paper'],
            'title' : 'Top 5 Movers',
            'titlefont' : dict(
                            size=25,
                            color=colors['Slate'])}

    }
    
#--------------------------------------------------------------------------------------------------------------------------- 
#---------------------------------------------------------------------------------------------------------------------------

@app.callback(
    dash.dependencies.Output('pie2','figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value')])
def update_pie2(tickers):
    
    labels = df_table_top['Ticker'][:-5]
    values = df_table_top['5 Day % Change'][:-5]
        
    trace = [go.Pie(
                labels=labels, 
                values=values,
                hole='0.6',
                textinfo='none',
                textfont=dict(size=20),
                #textposition='outside',
                marker={'colors': [colors['FT Claret'],
                                   colors['FT Pink Tint 2'],
                                   colors['Slate'],
                                   colors['Oxford'],
                                   colors['FT Light Blue']]}

            )]
   
    return{
        'data': trace,        
        'layout': {
            'plot_bgcolor': colors['Paper'],
            'paper_bgcolor': colors['Paper'],
            'title' : 'Top 5 Movers again',
            'titlefont' : dict(
                            size=25,
                            color=colors['Slate'])}

    }
    


if __name__ == '__main__':
    app.run_server(debug=True)
