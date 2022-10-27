from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# stylesheet with the .dbc class
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

load_figure_template("flatly")

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])


def df_prepare(val, colms):
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


df_res = df_prepare('tblGegevens.csv', ['pdssr', 'pdpsr', 'pda', 'pdc', 'Date']).dropna(subset=['Radars'])

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
        dcc.Graph(id='indicator-graphic'),
        dcc.Graph(id='indicator-graphic2'),
        dcc.Graph(id='indicator-graphic3')
    ]),

],
    className='dbc',
)


def make_graph(radar_name, type, colms):
    df = df_prepare('tblGegevens.csv', colms)
    df = df[df['Radars'] == radar_name]

    df = df.drop(df.columns[0], axis=1)

    for i in range(1, len(df.columns)):
        df[df.columns[i]] = df[df.columns[i]].astype(float)

    # sort by date
    df = df.sort_values(by=['Date'])
    df = df[df['Date'] < datetime.now().strftime('%Y-%m-%d')]

    # move . one place to the left if value is above 100
    # for i in range(1, len(df.columns)):
    #    df[df.columns[i]] = df[df.columns[i]].apply(lambda x: x / 10 if x > 100 else x)

    # add percentage to value

    if type != 'Biases':
        for i in range(1, len(df.columns)):
            df[df.columns[i]] = df[df.columns[i]].apply(lambda x: x / 100)

    # only keep the columns in colms
    df = df[colms]



    fig = px.line(df, x="Date", y=df.columns,
                  title=radar_name + ' ' + type, markers=False, line_shape='linear', render_mode="webg1")

    fig.update_layout(
        legend_title="Stats",
        hovermode="x unified",
        yaxis_tickformat=',.2%' if type != 'Biases' else '',
        template='flatly',
        xaxis=dict(
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
            autorange=True
        )
    )

    return fig


@app.callback(
    [Output('indicator-graphic', 'figure'),
     Output('indicator-graphic2', 'figure'),
     Output('indicator-graphic3', 'figure')],
    Input('radar-name', 'value'))
def update_graph(radar_name, df=df_res):
    fig = make_graph(radar_name, 'Probability', ['pdssr', 'pdpsr', 'pda', 'pdc', 'Date'])
    fig2 = make_graph(radar_name, 'Errors', ['iva', 'ivc', 'fc', 'ft', 'mt', 'Date'])
    fig3 = make_graph(radar_name, 'Biases', ['rng', 'azim', 'Date'])

    return fig, fig2, fig3


if __name__ == '__main__':
    app.run_server(debug=True)
