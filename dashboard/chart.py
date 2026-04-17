from dash import Dash, Input, Output, callback, dcc, html
from dash import dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import os
from start_new_round import start_new_round
from api import get_api


SERVER = os.environ["GRIST_URL"]
DOC_ID = os.environ["GRIST_DOC_ID"]
API_TOKEN = os.environ["GRIST_API_TOKEN"]

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])


app.layout = dbc.Container([
    html.H3('Leaderboard'),
    dbc.Button(
        'Neue Runde',
        id='new-round-button',
        color='primary',
        className='mb-3'
    ),
    dcc.Graph(id='live-update-graph'),

    html.H4('Tische'),
    dash_table.DataTable(
        id='table',
        style_header={
            'backgroundColor': '#303030',
            'color': 'white',
            'fontWeight': 'bold'
            },
        style_data={
            'backgroundColor': '#1a1a1a',
            'color': 'white',
            },
        style_cell={
            'border': '1px solid #444'
            }
        ),
    dcc.Interval(
        id='interval-component',
        interval=0.5*1000, # in milliseconds
        n_intervals=0
        ),

    html.H4('Pause'),

    dash_table.DataTable(
        id='pause_table',
        style_header={
            'backgroundColor': '#303030',
            'color': 'white',
            'fontWeight': 'bold'
            },
        style_data={
            'backgroundColor': '#1a1a1a',
            'color': 'white',
            },
        style_cell={
            'border': '1px solid #444'
            }
        ),


    ], fluid=True, className='dashboard-container'
)


@callback(
    Output('table', 'data'),
    Output('table', 'columns'),
    Input('interval-component', 'n_intervals')
)
def update_table(n):
    api = get_api()
    rounds = api.fetch_table('Rounds')
    df = pd.DataFrame([r._asdict() for r in rounds])
    max_round = df.max()['Round']
    df = df[df['Round'] == max_round]
    df["SpielerIn 1"] = df["gristHelper_Display"]
    df["SpielerIn 2"] = df["gristHelper_Display2"]
    df["SpielerIn 3"] = df["gristHelper_Display3"]
    df = df.reset_index()
    df = df.reset_index()
    df["Tisch"] = df["level_0"] + 1


    df = df[["Tisch", "SpielerIn 1", "SpielerIn 2", "SpielerIn 3"]]
    columns = [{'name': col, 'id': col} for col in df.columns]

    return df.to_dict('records'), columns


@callback(
    Output('pause_table', 'data'),
    Output('pause_table', 'columns'),
    Input('interval-component', 'n_intervals')
)
def update_table(n):
    api = get_api()

    players = api.fetch_table('Players')
    player_df = pd.DataFrame.from_dict(players)
    player_df = player_df[player_df['Active'] == True]

    rounds = api.fetch_table('Rounds')
    round_df = pd.DataFrame([r._asdict() for r in rounds])
    max_round = round_df.max()['Round']
    round_df = round_df[round_df['Round'] == max_round]

    players_in_rounds = set(round_df['Player1']) | set(round_df['Player2']) | set(round_df['Player3'])
    player_df = player_df[~player_df['id'].isin(players_in_rounds)]


    player_df = player_df[['Name']]

    # player_df = player_df[round_df["Player1"] == player_df[id]]

    columns = [{'name': col, 'id': col} for col in player_df.columns]


    return player_df.to_dict('records'), columns


@callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    api = get_api()
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

    pivot = df.pivot(index="Player", columns="Round", values="Points").fillna(0)
    cum = pivot.cumsum(axis=1)

    melted = cum.melt(ignore_index=False)
    melted = melted.sort_values(['Round', 'value'], ascending=[False, False])
    melted["id"] = melted.index

    with_player = pd.merge(melted, players, on='id')
    with_player["Runde"] = with_player["Round"]
    with_player["Punkte"] = with_player["value"]


    # print()
    all_names = players.sort_values('id')['Name'].tolist()
    colors = px.colors.qualitative.Plotly  # or any palette you like
    color_map = {name: colors[i % len(colors)] for i, name in enumerate(all_names)}


    fig = px.line(
        with_player,
        x="Runde", y="Punkte",
        color="Name",
        markers=True,
        template="plotly_dark",
        color_discrete_map=color_map,
    )

    return fig


@callback(
    Input('new-round-button', 'n_clicks'),
)
def snr(n_clicks):
    start_new_round()


app.run(host="0.0.0.0", port=8050, debug=False)


