import dash
import dash_core_components as dcc
import dash_html_components as html

import datetime as dt
import pandas as pd
from pandas_datareader.data import DataReader
import plotly.graph_objs as go

app = dash.Dash()


df_symbol = pd.read_csv('tickers.csv')
app.config['suppress_callback_exceptions']=True	

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
                       }
        ),

    ],
    className='row'
    ),

	html.Div(
        [
        dcc.Dropdown(
            id='stock-ticker-input',
            options=[{'label': s[0], 'value': str(s[1])}
                     for s in zip(df_symbol.Company, df_symbol.Symbol)],
            value=['GOOGL'],
            multi=True
        ),
        ],
        className='row'
    ),


    html.Div(
        className="row",
        children=[
            html.Div(
                className="six columns",
                children=[
                    html.Div(
                    	children=dcc.Graph(id='graph1')

                        )
                    ]
            ),
               
            
            html.Div(
                className="six columns",
                children=html.Div([
                    dcc.Graph(
                        id='right-top-graph',
                        figure={
                            'data': [{
                                'x': [1, 2, 3],
                                'y': [3, 1, 2],
                                'type': 'bar'
                            }],
                            'layout': {
                                'height': 400,
                                'margin': {'l': 10, 'b': 20, 't': 0, 'r': 0}
                            }
                        }
                    ),
                    dcc.Graph(
                        id='right-bottom-graph',
                        figure={
                            'data': [{
                                'x': [1, 2, 3],
                                'y': [3, 1, 2],
                                'type': 'bar'
                            }],
                            'layout': {
                                'height': 400,
                                'margin': {'l': 10, 'b': 20, 't': 0, 'r': 0}
                            }
                        }
                    ),

                ])
            ),
        ]
    ),
])

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})



@app.callback(
    dash.dependencies.Output('graph1', 'figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value')])

	
def update_graph1(tickers):
    #print(ticker)
   
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

        candlestick = [{
            'x': df['Date'],
            'open': df['Open'],
            'high': df['High'],
            'low': df['Low'],
            'close': df['Close'],
            'type': 'candlestick',
            #'name': 'graph1',
            'name': ticker,
            'legendgroup': ticker,
            'increasing': {'line': {'color': '#228B22'}},
            'decreasing': {'line': {'color': '#FF0000'}}
        }]
		
    return{
            'data': candlestick# + bollinger_traces
			#x = [1,2,3,4,5],
			#y = [1,2,3,4,5],
			#mode = 'markers')]
    }
    

if __name__ == '__main__':
    app.run_server(debug=True)
