import dash
import dash_core_components as dcc
import dash_html_components as html

import colorlover as cl
import datetime as dt
import flask
import os
import pandas as pd
from pandas_datareader.data import DataReader
import time

app = dash.Dash('stock-tickers')
server = app.server

app.scripts.config.serve_locally = False
#dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-finance-1.28.0.min.js'

colorscale = cl.scales['9']['qual']['Paired']

df_symbol = pd.read_csv('tickers.csv')

app.layout = html.Div([
    html.Div([
        html.H2('Stock Explorer',
                style={'display': 'inline',
                       'float': 'left',
                       'font-size': '2.65em',
                       'margin-left': '7px',
                       'font-weight': 'bolder',
                       'font-family': 'Product Sans',
                       'color': "rgba(117, 117, 117, 0.95)",
                       'margin-top': '20px',
                       'margin-bottom': '0'
                       }),
        
    ]),
    dcc.Dropdown(
        id='stock-ticker-input',
        options=[{'label': s[0], 'value': str(s[1])}
                 for s in zip(df_symbol.Company, df_symbol.Symbol)],
        value=['GOOGL'],
        multi=True
    ),
	html.Div(id='graph1'),
    html.Div(id='graph2'),
], className="container")

def bbands(price, window_size=10, num_of_std=5):
    rolling_mean = price.rolling(window=window_size).mean()
    rolling_std  = price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std*num_of_std)
    lower_band = rolling_mean - (rolling_std*num_of_std)
    return rolling_mean, upper_band, lower_band

app.config['suppress_callback_exceptions']=True	
	
@app.callback(
    dash.dependencies.Output('graph1','children'),
    [dash.dependencies.Input('stock-ticker-input', 'value')])

	
def update_graph1(tickers):
    graph1 = []
    for i, ticker in enumerate(tickers):
        try:
            df = DataReader(str(ticker), 'morningstar',
                            dt.datetime(2017, 1, 1),
                            dt.datetime.now()).reset_index()
        except:
            graph1.append(html.H3(
                'Data is not available for {}'.format(ticker),
                style={'marginTop': 20, 'marginBottom': 20}
            ))
            continue

        candlestick = {
            'x': df['Date'],
            'open': df['Open'],
            'high': df['High'],
            'low': df['Low'],
            'close': df['Close'],
            'type': 'candlestick',
            'name': ticker,
            'legendgroup': ticker,
            'increasing': {'line': {'color': '#228B22'}},
            'decreasing': {'line': {'color': '#FF0000'}}
        }
		
        bb_bands = bbands(df.Close)
		
        bollinger_traces = [{
            'x': df['Date'], 'y': y,
            'type': 'scatter', 'mode': 'lines',
            'line': {'width': 1, 'color': colorscale[(i*2) % len(colorscale)]},
            'hoverinfo': 'none',
            'legendgroup': ticker,
            'showlegend': True if i == 0 else False,
            'name': '{} - bollinger bands'.format(ticker)
        } for i, y in enumerate(bb_bands)]
		
        graph1.append(dcc.Graph(
            id=ticker,
            figure={
                'data': [candlestick] + bollinger_traces,
                'layout': {
                    'margin': {'b': 0, 'r': 30, 'l': 60, 't': 0},
                    'legend': {'x': 0}
                }
            }
        ))

    return graph1
	
@app.callback(
    dash.dependencies.Output('graph2','children'),
    [dash.dependencies.Input('stock-ticker-input', 'value')])
	
def update_graph2(tickers):
    graph2 = []
    for i, ticker in enumerate(tickers):
        try:
            df = DataReader(str(ticker), 'morningstar',
                            dt.datetime(2017, 1, 1),
                            dt.datetime.now()).reset_index()
        except:
            graph2.append(html.H3(
                'Data is not available for {}'.format(ticker),
                style={'marginTop': 20, 'marginBottom': 20}
            ))
            continue
		
        volume = {
			'x': df['Date'],
			'y': df['Volume'],
			'legendgroup': ticker,
			'type': 'bar',
			'showlegend': True
		}

        graph2.append(dcc.Graph(
            id='volume',
            figure={
                'data': [volume],
                'layout': {
                    'margin': {'b': 80, 'r': 30, 'l': 60, 't': 0},
                    'legend': {'x': 0}
                }
            }
        ))

    return graph2



if __name__ == '__main__':
    app.run_server(debug=True)