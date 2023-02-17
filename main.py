from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# stylesheet with the .dbc class
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

list_probabilities = ['pdssr', 'pdpsr', 'pda', 'pdc']
list_errors = ['iva', 'ivc', 'fc', 'ft', 'mt']
list_biases = ['rng', 'azim']

load_figure_template("flatly")

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])


def df_prepare(val):
    df_prep = pd.read_csv(val, sep=';')
    df_prep = df_prep.drop(df_prep.columns[-1:], axis=1)
    df_prep = df_prep.replace(';', ',', regex=True)
    df_prep = df_prep.replace(',', '.', regex=True)
    # drop time from date
    df_prep['Date'] = df_prep['Date'].str.split(' ').str[0]
    # convert date to datetime
    df_prep['Date'] = pd.to_datetime(df_prep['Date'], format='%d/%m/%Y')

    # drop all rows older than five years
    df_prep = df_prep[df_prep['Date'] > datetime.now() - relativedelta(years=5)]

    return df_prep


df_res = df_prepare('tblGegevens.csv')

app.layout = dbc.Container([

    html.H1('Radar stats', className='text-center'),
    html.Div([
        html.Div([

            dcc.Dropdown(
                df_res['Radars'].unique(),
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
    df = df_prepare('tblGegevens.csv')
    df = df[df['Radars'] == radar_name]
    df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    df = df.drop(df.columns[0], axis=1)

    for i in range(1, len(df.columns)):
        df[df.columns[i]] = df[df.columns[i]].astype(float)

    # sort by date
    df = df.sort_values(by=['Date'])
    df = df[df['Date'] < datetime.now().strftime('%Y-%m-%d')]

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.3, 0.3, 0.3])

    # add traces for list_probabilities
    for i in range(0, len(list_probabilities)):
        fig.add_trace(go.Scatter(x=df['Date'], y=df[list_probabilities[i]], name=list_probabilities[i], ), 1, 1)
    # add traces for list_errors
    for i in range(0, len(list_errors)):
        fig.add_trace(go.Scatter(x=df['Date'], y=df[list_errors[i]], name=list_errors[i]), 2, 1)
    # add traces for list_biases
    for i in range(0, len(list_biases)):
        fig.add_trace(go.Scatter(x=df['Date'], y=df[list_biases[i]], name=list_biases[i]), 3, 1)

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
