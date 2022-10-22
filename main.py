from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
from datetime import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

df_prep = pd.read_csv('tblGegevens.csv', sep=';')

df_prep = df_prep.drop(df_prep.columns[-5:], axis=1)
df_prep = df_prep.replace(';', ',', regex=True)
df_prep = df_prep.replace(',', '.', regex=True)
df_prep = df_prep.dropna(subset=['Radars'])
# drop time from date
df_prep['Date'] = df_prep['Date'].str.split(' ').str[0]
# convert date to datetime
df_prep['Date'] = pd.to_datetime(df_prep['Date'], format='%d/%m/%Y')

# drop all rows older than five years
df_prep = df_prep[df_prep['Date'] > datetime.now() - relativedelta(years=5)]

app.layout = html.Div([
    html.Div([

        html.Div([
            dbc.Select(
                id='radar-name',
                options=[{'label': name, 'value': name} for name in df_prep['Radars'].unique()],
                value='S723E'
            )

        ], style={'width': '10em', "display": 'inline-block', 'margin-right': 'auto',
                  'margin-left': '1em'}),
        dcc.Graph(id='indicator-graphic',
                  style={'backgroundColor': '#111111', 'height': '80vh', 'padding': '1em',
                         'border': '1px solid #222222', 'border-radius': '5px', 'margin': '1em'}),
    ], style={'backgroundColor': '#111111', 'height': '80vh', 'padding': '1em'}),

], style={'padding': '5em', 'height': '100vh', 'backgroundColor': '#111111'})


@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('radar-name', 'value'))
def update_graph(radar_name, df=df_prep):
    df = df[df['Radars'] == radar_name]

    df = df.drop(df.columns[0], axis=1)

    for i in range(1, len(df.columns)):
        df[df.columns[i]] = df[df.columns[i]].astype(float)

    # sort by date
    df = df.sort_values(by=['Date'])
    df = df[df['Date'] < datetime.now().strftime('%Y-%m-%d')]

    # move . one place to the left if value is above 100
    for i in range(1, len(df.columns)):
        df[df.columns[i]] = df[df.columns[i]].apply(lambda x: x / 10 if x > 100 else x)

    # add percentage to value
    for i in range(1, len(df.columns)):
        df[df.columns[i]] = df[df.columns[i]].apply(lambda x: x / 100)

    fig = px.line(df, x="Date", y=df.columns,
                  title=radar_name, markers=False, line_shape='linear', render_mode="webg1")
    fig.update_xaxes(

    )

    fig.update_layout(
        legend_title="Stats",
        hovermode="x unified",
        yaxis_tickformat=',.2%',
        template='plotly_dark',
        xaxis=dict(
            tickformat="%b\n%Y", rangeslider_visible=True, rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ]), bgcolor='#515151', bordercolor='#515151', borderwidth=1, font=dict(color='white')
            ), tickformatstops=[
                dict(dtickrange=[None, 1000], value="%H:%M:%S.%L ms"),
                dict(dtickrange=[1000, 60000], value="%H:%M:%S s"),
                dict(dtickrange=[60000, 3600000], value="%H:%M m"),
                dict(dtickrange=[3600000, 86400000], value="%H:%M h"),
                dict(dtickrange=[86400000, 604800000], value="%e %b"),
                dict(dtickrange=[604800000, "M1"], value="%e %b"),
                dict(dtickrange=["M1", "M12"], value="%b '%y"),
                dict(dtickrange=["M12", None], value="%Y")
            ], minor=dict(ticks="inside", showgrid=True)
        )
    )

    fig.write_html('report.html', auto_open=False)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
