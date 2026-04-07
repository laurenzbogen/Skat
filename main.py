from grist_api import GristDocAPI
import pandas as pd
from random import random
from time import sleep
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

SERVER = "http://localhost:8484"
DOC_ID = "1vocMdgaeywkff6dfpFxbx"  # full docId, not the urlId

api = GristDocAPI(DOC_ID, server=SERVER, api_key="e1858b0c8bfa2d75c23c733846a8f213b7717375")

round_data = api.fetch_table('Rounds')
df = pd.DataFrame.from_dict(round_data)
current_round = int(df['Round'].max()) + 1 if 'Round' in df.columns else 1

data = api.fetch_table('Players')

df = pd.DataFrame.from_dict(data);
df = df.query('Active')
df = df.sort_values('AmountPlayed', key=lambda col: col.apply(lambda x: random() * 2 + x))
trimmed = df.iloc[:len(df) - len(df) % 3]
shuffled = trimmed.sample(frac=1).reset_index(drop=True)
groups = [shuffled.iloc[i:i+3] for i in range(0, len(trimmed), 3)]



for g in groups:
    rows = api.add_records('Rounds', [
        {'Player1': g.iloc[0].Name, 'Player2': g.iloc[1].Name, 'Player3': g.iloc[2].Name, 'Round': current_round},
    ])

