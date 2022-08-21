import dash
from jupyter_dash import JupyterDash
from dash import Dash, dcc, html, dcc, Input, Output, State
#from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
from datetime import datetime
from time import time, sleep
#import json
import plotly.io as pio
pio.renderers.default = "vscode"
import plotly.graph_objects as go
import plotly.express as px


# import data
roster = pd.read_csv('/Users/sofiahuang/Documents/pythonprojects/dashboard/roster.csv')
df_bw = pd.read_csv('/Users/sofiahuang/Documents/pythonprojects/dashboard/bodyweight.csv')
df_fly = pd.read_csv('/Users/sofiahuang/Documents/pythonprojects/dashboard/fly10-20.csv')
df_vj = pd.read_csv('/Users/sofiahuang/Documents/pythonprojects/dashboard/vertjump.csv')

# data preprocessing
df_bw.dropna(axis=0,inplace=True)
df_fly.dropna(axis=0,inplace=True)
df_vj.dropna(axis=0,inplace=True)

df_bw['DATE'] = pd.to_datetime(df_bw['DATE'])
df_bw['Weight'] = pd.to_numeric(df_bw['WEIGHT'])
df_fly['DATE'] = pd.to_datetime(df_fly['Date']).dt.normalize()
df_vj['DATE'] = pd.to_datetime(df_vj['Date'])
df_fly.rename(columns = {' Avg':'AVG'}, inplace = True)
df_fly['AVGMPH'] = pd.to_numeric(df_fly['MPH'])
df_vj.rename(columns = {' Avg':'AVG'}, inplace = True)
df_vj['AVGNUM'] = pd.to_numeric(df_vj['AVG'])

# create new column to determine semester
def create_sem_column(df):
    conditions = [
        (df['DATE'] >= datetime(2021, 1, 1)) & (df['DATE'] <= datetime(2021, 5, 1)),
        (df['DATE'] >= datetime(2021, 5, 31)) & (df['DATE'] <= datetime(2021, 8, 16)),
        (df['DATE'] >= datetime(2022, 1, 27)) & (df['DATE'] <= datetime(2022, 4, 25)),
        (df['DATE'] >= datetime(2022, 5, 31)) & (df['DATE'] <= datetime(2022, 8, 20))
        ]

    values = ['Spring 2021', 'Summer 2021', 'Spring 2022', 'Summer 2022']

    df['Semester'] = np.select(conditions, values)
    return df

df_bw = create_sem_column(df_bw)
df_vj = create_sem_column(df_vj)
df_fly = create_sem_column(df_fly)

# divide player data by position
db = np.unique(roster.loc[roster['POS'] == 'DB'].NAME).tolist()
lb = np.unique(roster.loc[roster['POS'] == 'LB'].NAME).tolist()
dl = np.unique(roster.loc[roster['POS'] == 'DL'].NAME).tolist()
ol = np.unique(roster.loc[roster['POS'] == 'OL'].NAME).tolist()
sp = np.unique(roster.loc[roster['POS'] == 'SP'].NAME).tolist()
wr = np.unique(roster.loc[roster['POS'] == 'WR'].NAME).tolist()
rb = np.unique(roster.loc[roster['POS'] == 'RB'].NAME).tolist()
te = np.unique(roster.loc[roster['POS'] == 'TE'].NAME).tolist()
qb = np.unique(roster.loc[roster['POS'] == 'QB'].NAME).tolist()
pos = np.unique(roster['POS']).tolist()
all_players = np.unique(roster['NAME']).tolist()
all_players_pos = {}
all_players_pos['ALL'] = all_players
all_players_pos['DB'] = db
all_players_pos['LB'] = lb
all_players_pos['DL'] = dl
all_players_pos['OL'] = ol
all_players_pos['SP'] = sp
all_players_pos['WR'] = wr
all_players_pos['RB'] = rb
all_players_pos['TE'] = te
all_players_pos['QB'] = qb

# create df with all necessary data
merge1 = pd.merge(df_fly,df_vj,how='outer')
merge2 = pd.merge(df_bw,merge1,how='outer')
merge2['Stat'] = np.where(merge2.WEIGHT.notnull(), 'Body Weight', np.where(merge2.AVGNUM.notnull(), 'Vert Jump', 'Fly Speed'))
merge2.rename(columns = {'Weight':'Body Weight','AVGNUM':'Vert Jump', 'AVGMPH':'Fly Speed'}, inplace = True)

# deploy dashboard
app = JupyterDash('SimpleExample')

fnameDict = all_players_pos

names = list(fnameDict.keys())
nestedOptions = fnameDict[names[0]]

app.layout = html.Div(
    [
        html.H1(children="W&M Football Statistics",),

        html.Div([
        dcc.Dropdown(
            id='name-dropdown',
            options=[{'label':name, 'value':name} for name in names],
            value = list(fnameDict.keys())[0]
            ),
            ],style={'width': '20%', 'display': 'inline-block'}),

        html.Div([
        dcc.Dropdown(
            id='opt-dropdown',
            ),
            ],style={'width': '20%', 'display': 'inline-block'}
        ),

        html.Div([
        dcc.Dropdown(
            id='stat-dropdown',
            options=[{'label': 'Body Weight', 'value': 'Body Weight'} ,
                 {'label': 'Vertical Jump','value': 'Vert Jump'} ,
                 {'label': 'Fly Speed','value': 'Fly Speed'}],
            ),
            ],style={'width': '20%', 'display': 'inline-block'}
        ),

        html.Div([
        dcc.Dropdown(
            id='semester-dropdown',
            options=[{'label': 'Spring 2021', 'value': 'Spring 2021'} ,
                 {'label': 'Summer 2021','value': 'Summer 2021'} ,
                 {'label': 'Spring 2022','value': 'Spring 2022'} ,
                 {'label': 'Summer 2022','value': 'Summer 2022'}],
            ),
            ],style={'width': '20%', 'display': 'inline-block'}
        ),

        html.Hr(),

        html.Div(id='display-selected-values'),

        dcc.Graph(
            id='graph1',
        ),

        html.H2(children="Recent Stats"),
        
        html.H4(id='recent-bw'),

        html.H4(id='recent-vj'),

        html.H4(id='recent-fl')
    ]
)

@app.callback(
    dash.dependencies.Output('opt-dropdown', 'options'),
    [dash.dependencies.Input('name-dropdown', 'value')]
)
def update_date_dropdown(name):
    return [{'label': i, 'value': i} for i in fnameDict[name]]

@app.callback(
    dash.dependencies.Output('display-selected-values', 'children'),
    [dash.dependencies.Input('opt-dropdown', 'value')])
def set_display_children(selected_value):
    return '{}'.format(selected_value)

@app.callback(
Output('graph1', 'figure'), 
[Input('opt-dropdown', 'value'),Input('stat-dropdown', 'value'),Input('semester-dropdown', 'value')]
)
#graph plot and styling
def update_graph(value, stat, sem):
    fig = px.line(merge2.loc[(merge2['NAME'] == value) & (merge2['Stat'] == stat) & (merge2['Semester'] == sem)], 
        x='DATE', y=stat, template="simple_white")
    fig.update_traces(line_color='rgb(17, 87, 64)')
    fig.update_layout(paper_bgcolor ='rgb(185,151,91)')
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgb(185,151,91)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgb(185,151,91)')
    return fig  

@app.callback(
    dash.dependencies.Output('recent-bw', 'children'),
    [dash.dependencies.Input('opt-dropdown', 'value')])
def show_recent_stats(value):
    if (value is not None):
        temp = merge2.loc[merge2['NAME']==value]

        bw_temp = temp.loc[temp['Stat']=='Body Weight']
        bw = bw_temp.loc[bw_temp['DATE'] == bw_temp['DATE'].max()]['Body Weight']

        if (len(bw.values) == 0): bw = 'No recent body weight'
        else: bw = 'Body Weight: ' + str(bw.values[0]) + ' lbs'

        return bw

@app.callback(
    dash.dependencies.Output('recent-vj', 'children'),
    [dash.dependencies.Input('opt-dropdown', 'value')])
def show_recent_stats(value):
    if (value is not None):
        temp = merge2.loc[merge2['NAME']==value]

        vj_temp = temp.loc[temp['Stat']=='Vert Jump']
        vj = vj_temp.loc[vj_temp['DATE'] == vj_temp['DATE'].max()]['Vert Jump']

        if (len(vj.values) == 0): vj = 'No recent vert jump'
        else: vj = 'Vert Jump: ' + str(vj.values[0]) + ' inches'

        return vj

@app.callback(
    dash.dependencies.Output('recent-fl', 'children'),
    [dash.dependencies.Input('opt-dropdown', 'value')])
def show_recent_stats(value):
    if (value is not None):
        temp = merge2.loc[merge2['NAME']==value]

        fl_temp = temp.loc[temp['Stat']=='Fly Speed']
        fly = fl_temp.loc[fl_temp['DATE'] == fl_temp['DATE'].max()]['Fly Speed']

        if (len(fly.values) == 0): fly = 'No recent fly speed'
        else: fly = 'Fly Speed: ' + str(fly.values[0]) + ' mph' 

        return fly


if __name__ == '__main__':
    app.run_server(debug=True)