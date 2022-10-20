import pandas as pd
import plotly.express as px

df = pd.DataFrame({'date': ['04/03/2022', '05/03/2022', '06/03/2022', '07/03/2022', '08/03/2022', '09/03/2022',
                            '10/03/2022'],
                   'PDPR': [81, 84, 80, 0, 0, 87, 88],
                   'PDSSR': [99, 97, 98, 81, 85, 99, 96]
                   })
fig = px.line(df, x="date", y=df.columns,
              title='EBSZ')
fig.update_xaxes(
    dtick="M1",
    tickformat="%b\n%Y")
fig.update_yaxes(
    range=[0, 100]
)
fig.update_layout(
    legend_title="Sensors"
)
fig.write_html("file.html")
print(px.data.stocks())
print(df)
