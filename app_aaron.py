import dash
import dash_core_components as dcc
import dash_html_components as html

import datetime as dt
import pandas as pd
from pandas_datareader.data import DataReader
import plotly.plotly as py
import plotly.graph_objs as go


app = dash.Dash()


external_css = [ "https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
        "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
        "//fonts.googleapis.com/css?family=Raleway:400,300,600",
        "https://codepen.io/ygkubrick/pen/KoZPvz.css", #this is the header formatting
        "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
        "https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]

for css in external_css:
    app.css.append_css({ "external_url": css })

external_js = [ "https://code.jquery.com/jquery-3.2.1.min.js",
        "https://codepen.io/plotly/pen/KmyPZr.js" ]

for js in external_js:
    app.scripts.append_script({ "external_url": js })

#app.css.append_css({'external url': 'https://codepen.io/aaron-moss/pen/GdeQyK.css'})

colors = {'background': '#ED3131'}

df_table = pd.read_csv('test_table.csv')
df_symbol = pd.read_csv('tickers.csv')

app.config['suppress_callback_exceptions']=True 

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

app.layout = html.Div(style={'backgroundColor': colors['background']}[
    
    html.Div([
    html.H2('Stock Explorer',
                style={'display': 'inline',
                       'float': 'center',
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
                className="eight columns",
                children=html.Div([
                    dcc.Graph(id='graph1'),
                    dcc.Graph(id='graph2')
       
            ])
            ),
            
            html.Div(
                className="four columns",
                children=html.Div([
                    generate_table(df_table),
                    dcc.Graph(id='graph3')
            ])               
            ),
        ]
    ),
])


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
   


@app.callback(
    dash.dependencies.Output('graph4', 'figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value')])
def update_graph1(tickers):
    #print(ticker)
   
    for i, ticker in enumerate(tickers):
        try:
            df = DataReader(str(ticker), 'morningstar',
                            dt.datetime(2017, 1, 1),
                            dt.datetime.now()).reset_index()
        except:
            graph4.append(html.H3(
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


@app.callback(
    dash.dependencies.Output('graph2','figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value')])
def update_graph2(tickers):
    #graph2 = []
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
        
        volume = [{
            'x': df['Date'],
            'y': df['Volume'],
            'legendgroup': ticker,
            'type': 'bar',
            'showlegend': True
        }]

        # graph2.append(dcc.Graph(
        #     id='graph2',
        #     figure={
        #         'data': [volume],
        #         'layout': {
        #             'margin': {'b': 80, 'r': 30, 'l': 60, 't': 0},
        #             'legend': {'x': 0}
        #         }
        #     }
        # ))

    return{
        'data': volume
    }



@app.callback(
    dash.dependencies.Output('graph3','figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value')])
    
def update_graph3(tickers):
    #graph2 = []
    for i, ticker in enumerate(tickers):
        try:
            df = DataReader(str(ticker), 'morningstar',
                            dt.datetime(2017, 1, 1),
                            dt.datetime.now()).reset_index()
        except:
            graph3.append(html.H3(
                'Data is not available for {}'.format(ticker),
                style={'marginTop': 20, 'marginBottom': 20}
            ))
            continue
        
        volume = [{
            'x': df['Date'],
            'y': df['Volume'],
            'legendgroup': ticker,
            'type': 'bar',
            'showlegend': True
        }]

        # graph2.append(dcc.Graph(
        #     id='graph2',
        #     figure={
        #         'data': [volume],
        #         'layout': {
        #             'margin': {'b': 80, 'r': 30, 'l': 60, 't': 0},
        #             'legend': {'x': 0}
        #         }
        #     }
        # ))

    return{
        'data': volume
    }

if __name__ == '__main__':
    app.run_server(debug=True)
