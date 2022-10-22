from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
from datetime import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

global df

df = pd.read_csv('tblGegevens.csv', sep=';')

df = df.drop(df.columns[-5:], axis=1)
df = df.replace(';', ',', regex=True)
df = df.replace(',', '.', regex=True)
df = df.dropna(subset=['Radars'])
# drop time from date
df['Date'] = df['Date'].str.split(' ').str[0]
# convert date to datetime
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

# drop all rows older than 2015
df = df[df['Date'] > '2015-01-01']




app.layout = html.Div([
    html.Div([

        html.Div([
            dbc.Select(
                id='radar-name',
                options=[{'label': name, 'value': name} for name in df['Radars'].unique()],
                value='S723E'
            )

        ], style={'width': '10em', 'display': 'inline-block'}),
        dcc.Graph(id='indicator-graphic',
                  style={'backgroundColor': '#3f51b5', 'height': '80vh', 'color': 'white', 'padding': '1em'}),
    ], style={'backgroundColor': '#3f51b5', 'height': '80vh', 'color': 'white', 'padding': '1em'}),

], style={'padding': '5em', 'color': '#7FDBFF', 'height': '100vh', 'backgroundColor': '#3f51b5'})


@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('radar-name', 'value'))
def update_graph(radar_name, df=df):



    df = df[df['Radars'] == radar_name]

    df = df.drop(df.columns[0], axis=1)

    for i in range(1, len(df.columns)):
        df[df.columns[i]] = df[df.columns[i]].astype(float)

    # sort by date
    df = df.sort_values(by=['Date'])

    # drop all rows with dates in the future use drype dtime64
    df = df[df['Date'] < datetime.now().strftime('%Y-%m-%d')]




    # move . one place to the left if value is above 100
    for i in range(1, len(df.columns)):
        df[df.columns[i]] = df[df.columns[i]].apply(lambda x: x / 10 if x > 100 else x)

    # add percentage to value
    for i in range(1, len(df.columns)):
        df[df.columns[i]] = df[df.columns[i]].apply(lambda x: x / 100)


    fig = px.line(df, x="Date", y=df.columns,
                  title=radar_name, markers=True)
    fig.update_xaxes(
        tickformat="%b\n%Y", rangeslider_visible=True, rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")

            ])
        ), tickformatstops=[
            dict(dtickrange=[None, 1000], value="%H:%M:%S.%L ms"),
            dict(dtickrange=[1000, 60000], value="%H:%M:%S s"),
            dict(dtickrange=[60000, 3600000], value="%H:%M m"),
            dict(dtickrange=[3600000, 86400000], value="%H:%M h"),
            dict(dtickrange=[86400000, 604800000], value="%e %b"),
            dict(dtickrange=[604800000, "M1"], value="%e %b"),
            dict(dtickrange=["M1", "M12"], value="%b '%y"),
            dict(dtickrange=["M12", None], value="%Y")
        ], minor=dict(ticks="inside", showgrid=True),
    )

    fig.update_layout(
        legend_title="Stats",
        hovermode="x unified",
        yaxis_tickformat=',.2%',
        xaxis_autorange=False
    )

    fig.update_traces(mode='lines')

    # stop graph at last date
    fig.update_xaxes(range=[df['Date'].min(), datetime.now()])

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
