from dash import Dash, Input, Output, callback, dcc, html
from dash import dash_table
import dash_bootstrap_components as dbc
from grist_api import GristDocAPI
import pandas as pd
import plotly.express as px
import os

SERVER = os.environ["GRIST_URL"]
DOC_ID = os.environ["GRIST_DOC_ID"]
API_TOKEN = os.environ["GRIST_API_TOKEN"]

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])




app.layout = dbc.Container([
    html.H4('Leaderboard'),
    dcc.Graph(id='live-update-graph'),
    # dash_table.DataTable(id='table'),
    dcc.Interval(
        id='interval-component',
        interval=0.5*1000, # in milliseconds
        n_intervals=0
    )
], fluid=True, className='dashboard-container')


# @callback(
#     Output('table', 'data'),
#     Output('table', 'columns'),
#     Input('interval-component', 'n_intervals')
# )
# def update_table(n):
#     players = api.fetch_table('Players')
#     players = pd.DataFrame.from_dict(players)
#     players = players[["Name", "TotalPoints", "AmountPlayed"]]
#     players = players.sort_values("TotalPoints", ascending=False)
#
#     data = players.to_dict('records')
#     columns = [{'name': col, 'id': col} for col in players.columns]
#
#     return data, columns

@callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    api = GristDocAPI(DOC_ID, server=SERVER, api_key=API_TOKEN)
    players = api.fetch_table('Players')
    players = pd.DataFrame.from_dict(players)
    players['Player'] = players['id']


    records = []
    data = api.fetch_table('Rounds')
    df = pd.DataFrame.from_dict(data)
    for _, row in df.iterrows():
        for i in ['1', '2', '3']:
            records.append({
                'Round': row['Round'],
                'Player': row[f'Player{i}'],
                'Points': row[f'P{i}_Points']
            })

    df = pd.DataFrame.from_dict(records)
    all_rounds = sorted(df['Round'].unique())


    pivot = df.pivot(index="Player", columns="Round", values="Points").fillna(0)
    cum = pivot.cumsum(axis=1)
    ranks = cum

    test = ranks.melt(ignore_index=False)
    test = test.sort_values(['Round', 'value'], ascending=[False, False])

    test["id"] = test.index


    with_player = pd.merge(test, players, on='id')

    fig = px.line(with_player, x="Round", y="value", color="Name", markers=True, template="plotly_dark")

    return fig

app.run(host="0.0.0.0", port=8050, debug=False)
