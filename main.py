from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import sqlite3

# stylesheet with the .dbc class
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

list_probabilities = ['PD_P', 'PD_S', 'PD_M', 'PD_PS', 'PD_PM']
#list_errors = ['iva', 'ivc', 'fc', 'ft', 'mt']
#list_biases = ['rng', 'azim']

load_figure_template("flatly")

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])

#get df from database
def df_get(file):
    conn = sqlite3.connect(file)
    df = pd.read_sql_query("SELECT * FROM tblGegevens", conn)
    #df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    return df

df_res = df_get('rdmData.db')

app.layout = dbc.Container([

    html.H1('Radar stats', className='text-center'),
    html.Div([
        html.Div([

            dcc.Dropdown(
                df_res['Radar Name'].unique(),
                'S723E',
                id='radar-name'
            ),

        ]),

        html.Div([
            dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=df_res['Date'].min(),
                max_date_allowed=df_res['Date'].max(),
                initial_visible_month=df_res['Date'].max(),
                start_date=df_res['Date'].min(),
                end_date=df_res['Date'].max(),
                display_format='DD/MM/YYYY',
                className='dbc',
            ),
            # add two radio buttons to select the type of graph
            dcc.RadioItems(
                options=[
                    {'label': 'Stats over radar', 'value': 'sor'},
                    {'label': 'Radars over stat', 'value': 'ros'},
                ],
                value='line',
                id='graph-type',
                labelStyle={'display': 'inline-block'}
            ),
        ], id='output-container-date-picker-range'),

        dcc.Graph(id='indicator-graphic', style={'height': '80vh'}),
    ]),

],
    className='dbc',
)

def make_graph(radar_name, start_date, end_date):
    df = df_res

    df = df[df['Radar Name'] == radar_name]
    # sort by date
    df = df.sort_values(by=['Date'])
    df = df[df['Date'] < datetime.now().strftime('%Y-%m-%d')]
    df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    #for i in range(2, len(df.columns)):
        #df[df.columns[i]] = df[df.columns[i]].astype(float)

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.3, 0.3, 0.3])

    # add traces for list_probabilities
    for i in range(0, len(list_probabilities)):
        fig.add_trace(go.Scatter(x=df['Date'], y=df[list_probabilities[i]], name=list_probabilities[i], ), 1, 1)
    # add traces for list_errors
    #for i in range(0, len(list_errors)):
        #fig.add_trace(go.Scatter(x=df['Date'], y=df[list_errors[i]], name=list_errors[i]), 2, 1)
    # add traces for list_biases
    #for i in range(0, len(list_biases)):
        #fig.add_trace(go.Scatter(x=df['Date'], y=df[list_biases[i]], name=list_biases[i]), 3, 1)

    fig.update_layout(
        # add a button to show last month
        legend_title="Stats",
        # title_text="Radar stats",
        hovermode="x unified",
        template="flatly",
        xaxis=dict(
            tickformatstops=[
                dict(dtickrange=[None, 1000], value="%H:%M:%S.%L ms"),
                dict(dtickrange=[1000, 60000], value="%H:%M:%S s"),
                dict(dtickrange=[60000, 3600000], value="%H:%M m"),
                dict(dtickrange=[3600000, 86400000], value="%H:%M h"),
                dict(dtickrange=[86400000, 604800000], value="%e %b"),
                dict(dtickrange=[604800000, "M1"], value="%e %b"),
                dict(dtickrange=["M1", "M12"], value="%b '%y"),
                dict(dtickrange=["M12", None], value="%Y")
            ], minor=dict(ticks="inside", showgrid=True),
            autorange=True
        ),  # end xaxis  definition

        xaxis3_rangeslider_visible=True,
        xaxis3_type="date"
    )

    return fig


@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('radar-name', 'value'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
)
def update_graph(radar_name, start_date, end_date):
    fig = make_graph(radar_name, start_date, end_date)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
