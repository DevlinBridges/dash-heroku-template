import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import json

url = 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json'
response = requests.get(url)
counties = json.loads(response.text)

nba_info = pd.read_csv('https://raw.githubusercontent.com/DevlinBridges/dash-heroku-template/master/nba_info.csv')

nba_final_cleaned_grouped = nba_info.groupby('fips').agg({
    'Team': lambda x: ', '.join(x),
    'Championships': 'sum',
    'Points': 'sum',
    'MVPs': 'sum',
    'Finals MVPs': 'sum',
    'All-NBA First Team Selections': 'sum',
    'Leading Scorer': 'sum'
}).reset_index()

markdown_text = '''
The National Basketball Association (NBA), considered the premier league in the sport, was founded in 1949 when the Basketball Association of America (BAA) and the the National Basketball League (NBL) merged. In 1976, the NBA merged once again, this time with the competing, and equally as prestigious, American Basketball Association (ABA).
Thanks to meticulous (although some might argue against that adjective) scorekeeping throughout basketball's history, we have statistics for the sport going back as far as 1946. While the scorekeeping and playstyle has evolved over the years, many of the main metrics (points, assists, rebounds, wins, losses, championships) have stayed the same.
There's a contingent of basketball fans who argue against the datafication of basketball, saying it ruins the passion behind the game, reducing players down to numbers and turning fans into boxscore watchers instead of watching games. Like everything in life, I think there's a happy medium to be found between use of analytics in the sport and
use of the "eye test." Blog boys and pure hoopers continue to clash to this day, waging a war between efficient field goal percentage and "that man can ball". Premium shot selection vs. vibes. PER against "he went off this season."

This dashboard has nothing to do with that. It's just a fun exercise to explore some of the data available and look at some of the mainstay metrics (albeit very generic ones). It's my first time making a dashboard and all of the data was pulled from [Basketball Reference](https://www.basketball-reference.com/) and [Stathead](https://stathead.com/all/).
I did my best to clean the data with what I saw as glaring mistakes (the Pistons did not score 0 points in their history, as miserable as recent years might have been) but I'm sure there are some things missing.

I hope you have fun looking at generic measures that you could've just as easily have Googled.

Love and Basketball,
Devlin
'''

def countymap(col):
    fig = px.choropleth(
        nba_final_cleaned_grouped,
        geojson=counties,
        scope='usa',
        locations='fips',
        featureidkey="id",
        color=col,
        color_continuous_scale='reds',
        hover_name='Team',
        hover_data=['Points', 'MVPs', 'Finals MVPs', 'All-NBA First Team Selections', 'Leading Scorer'],
        title='NBA Teams'
    )
    
    fig.update_geos(fitbounds='locations', visible=True)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    return fig

def totalpoints(col):
    fig = px.bar(nba_info, x='Points', y='Team', color='Team',
                 labels={'Team':'NBA Team', 'Points':'Points Scored in Team History'},
                 title='Total Points Scored by Each NBA Team')
    fig.update_layout(showlegend=False)
    fig.update(layout=dict(title=dict(x=0.5)))
    return fig

def barchart(col):
    fig = px.bar(nba_info,
                 x='State',
                 y='Percentage of Points Scored',
                 color=col,
                 text='text',
                 labels={'State':'State', 'Percentage of Points Scored':'Percent'},
                 title='Percentage of Total Points Scored by State in NBA History',
                 hover_data=['Team', 'Championships', 'Leading Scorer', 'All-NBA First Team Selections', 'MVPs', 'Finals MVPs'])
    fig.update_traces(marker=dict(line=dict(width=2)))
    fig.update(layout=dict(title=dict(x=0.5)))
    return fig

def scatter(col1, col2):
    fig = px.scatter(nba_info,
                     x='Championships',
                     y=col1,
                     trendline='ols',
                     color='Team',
                     size=col2,
                     hover_data=['Team','Leading Scorer','MVPs','Finals MVPs'],
                     title='# of Championships Against...',
                     height=800, width=800)
    fig.update_layout(showlegend=True)
    return fig

def scatter2(col1, col2):
    fig = px.scatter(nba_info,
                     x=col1,
                     y=col2,
                     trendline='ols',
                     color='Team',
                     color_continuous_scale='Turbo',
                     size='Championships',
                     hover_data=['Team','Leading Scorer','MVPs','Finals MVPs'],
                     title='',
                     height=800, width=800,
                     size_max=15)
    fig.update_layout(showlegend=True)
    return fig

def table(col1):
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(nba_info.columns),
                    fill_color='lavender',
                    align='left'),
        cells=dict(values=[nba_info[col] for col in nba_info.columns],
                   fill_color='lightgrey',
                   align='left'))
    ])
    fig.update_layout(
        autosize=False,
        width=1200,
        height=800,
        margin=dict(l=10, r=10, b=10, t=10),
    )
    return fig

app = dash.Dash(__name__)

server = app.server  # Expose the server variable for deployment

app.layout = html.Div([
    html.H1("NBA Dashboard", style={'text-align': 'center'}),

    html.Img(src='https://upload.wikimedia.org/wikipedia/commons/6/6b/DeShawn_Stevenson_2.jpg', 
             style={'height': '400px', 'width': 'auto', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}),

    dcc.Markdown(markdown_text),

    html.P("Select the type of visualization:", style={'font-weight': 'bold'}),
    dcc.Dropdown(
        id='visualization-dropdown',
        options=[
            {'label': 'County Map', 'value': 'countymap'},
            {'label': 'Barchart', 'value': 'barchart'},
            {'label': 'Scatter Plot 1', 'value': 'scatter'},
            {'label': 'Scatter Plot 2', 'value': 'scatter2'},
            {'label': 'Table', 'value': 'table'}
        ],
        value='countymap'  # Default value
    ),

    html.P("Select the first variable (for Scatterplot 1, this controls y-axis; for Scatterplot 2, this controls x-axis):", style={'font-weight': 'bold'}),
    dcc.Dropdown(
        id='variable-dropdown',
        value='Points',  # Default value
        multi=False
    ),

    html.P("Select the first variable (for Scatterplot 1, this controls point size; for Scatterplot 2, this controls y-axis):", style={'font-weight': 'bold'}),
    dcc.Dropdown(
        id='variable2-dropdown',  # Second dropdown for col2
        value='Championships',  # Default value
        multi=False
    ),

    dcc.Graph(id='map')
])

@app.callback(
    Output('variable-dropdown', 'options'),
    Input('visualization-dropdown', 'value')
)
def update_variable_options(selected_visualization):
    if selected_visualization == 'countymap':
        allowed_columns = ['Championships', 'Points', 'MVPs', 'Finals MVPs', 'All-NBA First Team Selections']
    elif selected_visualization == 'barchart':
        allowed_columns = ['Points', 'MVPs', 'Finals MVPs', 'All-NBA First Team Selections', 'Yrs Existed']
    elif selected_visualization == 'scatter':
        allowed_columns = ['Founded', 'Points', 'MVPs', 'Finals MVPs', 'All-NBA First Team Selections', 'Yrs Existed', 'Championships']
    elif selected_visualization == 'scatter2':
        allowed_columns = ['Founded', 'Points', 'MVPs', 'Finals MVPs', 'All-NBA First Team Selections', 'Yrs Existed', 'Championships']
    else:
        allowed_columns = []
    
    # Return the new options for the variable-dropdown
    return [{'label': col, 'value': col} for col in allowed_columns]

@app.callback(
    Output('map', 'figure'),
    [Input('visualization-dropdown', 'value'),
     Input('variable-dropdown', 'value'),
     Input('variable2-dropdown', 'value')]  # Third argument for second dropdown
)
def update_figure(selected_visualization, col1, col2):
    if selected_visualization == 'countymap':
        return countymap(col1)
    elif selected_visualization == 'barchart':
        return barchart(col1)
    elif selected_visualization == 'scatter':
        return scatter(col1, col2)  # Pass both columns
    elif selected_visualization == 'scatter2':
        return scatter2(col1, col2)  # Pass both columns
    elif selected_visualization == 'table':
        return table(col1)
    else:
        return countymap(col1)  # Default to county map if something goes wrong
    
@app.callback(
    Output('variable2-dropdown', 'options'),
    Input('visualization-dropdown', 'value')
)
def update_variable2_options(selected_visualization):
    if selected_visualization in ['scatter','scatter2']:
        allowed_columns = ['Founded', 'Points', 'MVPs', 'Finals MVPs', 'All-NBA First Team Selections', 'Yrs Existed', 'Championships', 'Finals MVPs']
    else:
        allowed_columns = []  # Just use an empty list if not scatter or scatter2
    
    # Return the new options for the variable-dropdown
    return [{'label': col, 'value': col} for col in allowed_columns] or [{'label': 'N/A', 'value': 'N/A'}]
    
if __name__ == '__main__':
    app.run_server(debug=True)
