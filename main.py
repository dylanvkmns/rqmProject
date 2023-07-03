from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from datetime import datetime
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import sqlite3


def main():
    app.run_server(debug=True)


# stylesheet with the .dbc class
dbc_css = './assets/dbc.min.css'

list_probabilities = ['PD_P', 'PD_S', 'PD_M', 'PD_PS', 'PD_PM']

load_figure_template("minty")

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])

def df_get(file):
    conn = sqlite3.connect(file)
    df = pd.read_sql_query("SELECT * FROM tblGegevens", conn)
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y')  # y for yy Y for YYYY
    return df

df_res = df_get('rdmData.db')

app.layout = dbc.Container([

    html.H1('RDQE', className=''),
    html.Div([
        html.Div([
            dcc.RadioItems(
                options=[
                    {'label': 'Stats over radar', 'value': 'sor'},
                    {'label': 'Radars over stat', 'value': 'ros'},
                ],
                value='sor',
                id='graph-type',
                labelStyle={'display': 'inline-block'}
            ),
            dcc.Dropdown(
                options=[
                    {'label': 'PD_P', 'value': 'PD_P'},
                    {'label': 'PD_S', 'value': 'PD_S'},
                    {'label': 'PD_M', 'value': 'PD_M'},
                    {'label': 'PD_PS', 'value': 'PD_PS'},
                    {'label': 'PD_PM', 'value': 'PD_PM'}
                ],
                value='PD_P',
                id='stats-name'
            ),
        ], id='output-container-graph-type', className="align-centre"),

        dcc.Dropdown(
            df_res['Radar Name'].unique(),
            'S723_EBSZ',
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
    ], id='output-container-date-picker-range', className="align-centre"),

    dcc.Graph(id='indicator-graphic', style={'height': '80vh'}),

], className='dbc')


def make_graph(graph_type, radar_name, stats_name, start_date, end_date):
    df = df_res

    df = df.sort_values(by=['Date'])
    df = df[df['Date'] < datetime.now().strftime('%Y-%m-%d')]
    df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    num_stats = len(list_probabilities)

    fig = make_subplots(rows=num_stats, cols=1, shared_xaxes=True, subplot_titles=list_probabilities, vertical_spacing=0.1)

    if graph_type == 'sor':
        for i, stat in enumerate(list_probabilities):
            for radar in df['Radar Name'].unique():
                radar_df = df[df['Radar Name'] == radar]
                fig.add_trace(go.Scatter(x=radar_df['Date'], y=radar_df[stat], name=f'{radar} - {stat}'), row=i+1, col=1)
    elif graph_type == 'ros':
        for i, stat in enumerate(list_probabilities):
            fig.add_trace(go.Scatter(x=df['Date'], y=df[stat], name=stat), row=i+1, col=1)

    fig.update_layout(
        legend_title="Stats",
        hovermode="x unified",
        template="minty",
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
        ),

        xaxis3_rangeslider_visible=True,
        xaxis3_type="date"
    )

    return fig




@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('graph-type', 'value'),
    Input('radar-name', 'value'),
    Input('stats-name', 'value'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
)
def update_graph(graph_type, radar_name, stats_name, start_date, end_date):
    fig = make_graph(graph_type, radar_name, stats_name, start_date, end_date)
    return fig


if __name__ == '__main__':
    main()
