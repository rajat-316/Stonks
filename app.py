import dash
from dash import dcc
from dash import html
from datetime import datetime as dt

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

from model import prediction


app = dash.Dash(__name__)
server = app.server

#two divisions
app.layout = html.Div([
     
        html.Div(
        [   html.Img(src="https://img-9gag-fun.9cache.com/photo/a6OPpNb_460s.jpg", className='Image'),
            html.P("Visualizing and Forecasting of Stocks!", className="start"),

            html.Div([
                #stock input code
                html.P('Input stock code:'),
                dcc.Input(id="code",type="text",placeholder="Stock Code",className="box"),
                html.Button('Submit', id='Submit',className='button')
            ]),

            html.Div([html.Div("Select Date Range: "),
                # Date range picker input
                dcc.DatePickerRange(
                    id="date-picker-single",
                    min_date_allowed=dt(1985, 8, 5),
                    max_date_allowed=dt.now(),
                    initial_visible_month=dt.now(),
                    end_date=dt.now().date()),
            ]),
            html.Div([
                # Stock price button
                html.Button('Stock price', id='Stock price',className='button'),
                # Indicators button
                html.Button('Indicators', id='Indicators',className='button'),
                # Number of days of forecast input
                html.Div("Enter number of Days: "),
                dcc.Input(placeholder='Number of days',type='text',id='days',className="box"),
                # Forecast button
                html.Button('Forecast', id='Forecast',className='button')
            ])
            
        ],className="nav"),

    html.Div(
        [
            html.Div(
            [   # Logo
                html.Img(id="logo"),
                # Company Name
                html.P(id="company_name", className="start"),    
            ],            className="header"),
            #Description
            html.Div(id="description", className="decription_ticker"),
            # Stock price plot
            html.Div([], id="graphs-content"),
            # Indicator plot
            html.Div([], id="main-content"),
            # Forecast plot
            html.Div([], id="forecast-content")
        ],className="content")


],className="container")

@app.callback([
    Output("description", "children"),
    Output("logo","src"),
    Output("name","children"),
    Output("stock-button","n_clicks"),
    Output("indicators-button","n_clicks"),
    Output("forcast-button","n_clicks")
    ],
    [
    Input("submit","n_clicks")
    ],
    [
    State("stockcode", "value")
    ])
def update_data(name,code):  # input parameter(s)
    # your function here
    if code == None:
        return "This is a single-page web application using Dash (a python framework) which will show company information (logo, registered name and description) and stock plots based on the stock code given by the user. Also it contains an ML model will enable the user to get predicted stock prices for the date inputted by the user.","https://www.aegonlife.com/insurance-investment-knowledge/wp-content/uploads/2019/08/shutterstock_601834022.jpg","Stock Prediction",None,None,None
    ticker = yf.Ticker(code)
    inf = ticker.info
    df = pd.DataFrame().from_dict(inf, orient="index").T
    return df["longBusinessSummary"].values[0], df["logo_url"].values[0], df["shortName"].values[0],None,None,None

@app.callback([
    Output("graph-content","children")
    ],
    [
    Input("stock-button","n_clicks"),
    Input("date-picker","start_date"),
    Input("date-picker","end_date"),
    ],
    [State("stockcode","value")]
    )

def graph_plot(n,startdate,enddate,code):
    if n==None:
        return[""]
    if code == None:
        return [""]
    else:
        if startdate != None:
            df = yf.download(code, str(startdate), str(enddate))
        else:
            df = yf.download(code)
    df.reset_index(inplace=True)
    fig=get_stock_price_fig(df)
    return [dcc.Graph(figure=fig)]

def get_stock_price_fig(df):
    fig=px.line(df,x="Date",y=["Close","Open"],title="Closing and Opening Price vs Date")
    return fig

@app.callback([
    Output("main-content","children")
    ],
    [
    Input("indicators-button","n_clicks"),
    Input("date-picker","start_date"),
    Input("date-picker","end_date")
    ],
    [
    State("stockcode","value")
    ]
)

def ind_plot(n,startdate,enddate,code):
    if n== None:
        return[""]
    if code == None:
        return [""]
    if startdate != None:
        df = yf.download(code, str(startdate), str(enddate))
    else:
        df = yf.download(code)
    df.reset_index(inplace=True)
    fig=get_mode(df)
    return [dcc.Graph(figure=fig)]

def get_mode(df):
    df["EWA_20"]=df['Close'].ewm(span=20,adjust=False).mean()
    fig=px.scatter(df,
        x="Date",
        y="EWA_20",
        title="Exponential Moving Average vs Date")
    fig.update_traces(mode='lines+markers')
    return fig

@app.callback([Output("forcast-content", "children")],
              [Input("forcast-button", "n_clicks")],
              [State("input-Forcast", "value"),
               State("stockcode", "value")])
def forecast(n, n_days, val):
    if n == None:
        return [""]
    if val == None:
        return [""]
    fig = prediction(val, int(n_days) + 1)
    return [dcc.Graph(figure=fig)]


if __name__ == '__main__':
    app.run_server(debug=True)
