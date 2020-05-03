import dash
import dash_core_components as dcc
import dash_html_components as html
import altair as alt
import vega_datasets as vega
import pandas as pd
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import requests
import ast


app = dash.Dash(__name__, assets_folder='assets', external_stylesheets=[dbc.themes.CERULEAN])
app.config['suppress_callback_exceptions'] = True
server = app.server

app.title = 'Dash app with pure Altair HTML'
alt.data_transformers.disable_max_rows()

df = vega.data.jobs()
def mds_special():
    
        font = "Arial"
        axisColor = "#000000"
        gridColor = "#DEDDDD"
        return {
            "config": {
                "title": {
                    "fontSize": 24,
                    "font": font,
                    "anchor": "middle",
                    "fontColor": "#000000"
                },
                'view': {
                    "height": 300, 
                    "width": 400
                },
                "axisX": {
                    "domain": True,
                    #"domainColor": axisColor,
                    "gridColor": gridColor,
                    "domainWidth": 1,
                    "grid": False,
                    "labelFont": font,
                    "labelFontSize": 12,
                    "labelAngle": 0, 
                    "tickColor": axisColor,
                    "tickSize": 5, # default, including it just to show you can change it
                    "titleFont": font,
                    "titleFontSize": 16,
                    "titlePadding": 10, # guessing, not specified in styleguide
                    "title": "X Axis Title (units)", 
                },
                "axisY": {
                    "domain": False,
                    "grid": True,
                    "gridColor": gridColor,
                    "gridWidth": 1,
                    "labelFont": font,
                    "labelFontSize": 14,
                    "labelAngle": 0, 
                    #"ticks": False, # even if you don't have a "domain" you need to turn these off.
                    "titleFont": font,
                    "titleFontSize": 16,
                    "titlePadding": 50, # guessing, not specified in styleguide
                    "title": "Y Axis Title (units)", 
                    # titles are by default vertical left of axis so we need to hack this 
                    #"titleAngle": 0, # horizontal
                    #"titleY": -10, # move it up
                    #"titleX": 18, # move it to the right so it aligns with the labels 
                },
            }
                }

# register the custom theme under a chosen name
alt.themes.register('mds_special', mds_special)

# enable the newly registered theme
alt.themes.enable('mds_special')

# plotting the ratio bar chart
def map(business_to_choose = "Beauty Salon", year_to_choose = 2018):
    """
    Given the business type and year, filter the dataset and plot a map for the counts of the buisness per neighbourhood

    parameters 
    --------------------
    business_to_choose: (str)
            type of business to filter the dataset
    year_to_choose: (int)
            year to filter the dataset
    returns
    ---------------------
    an altair map.
    """
    dataset = pd.read_csv("Data/dataset.csv").dropna(subset=['Geom', 'LocalArea'])[["FOLDERYEAR", "LicenceRSN", "LocalArea", "Business_type_pp", "X", "Y"]]
    dataset_subset = dataset.query("Business_type_pp == @business_to_choose and FOLDERYEAR == @year_to_choose")
    url = "https://maps.vancouver.ca/server/rest/services/Hosted/NeighbourhoodBoundaries/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"
    # Vancouver Map Json file
    r = requests.get(url)
    file = r.json()
    background_data = alt.Data(values=file['features'])

    # Vancouver Background
    background = alt.Chart(background_data).mark_geoshape(
        fill='lightgray',
        stroke='white'
        ).encode(
        ).properties(
        width=500,
        height=300
    )

    # Obtaining the mean coordinates per LocalArea
    dataset_subset_grouped = dataset_subset.groupby(by = "LocalArea").aggregate({"LicenceRSN": 'count', "X": "mean", "Y": "mean"}).reset_index()
    points = alt.Chart(dataset_subset_grouped).mark_circle().encode(
    longitude='X:Q',
    latitude='Y:Q',
    size=alt.Size('LicenceRSN:Q', title='Number of ' + business_to_choose),
    color=alt.value('steelblue'),
    tooltip = ["LocalArea", "LicenceRSN"]
    ).properties(
        title='Number of '+ business_to_choose + ' Registered Businesses in Vancouver per Neighbourhood'
    )
    return background + points

# Add App Header
header = dbc.Row([
    dbc.Col(dbc.Jumbotron(
    [
        dbc.Container(
            [   html.H1(),
                html.H1("Vancouver Business Landscape", style={'margin-left': '30%'}),
                html.P(
                       "This is an interactive dashboard Visualizing The distribution of newly registered businesses in Vancouver, BC.  Choose the type of business and the year to get the count per local area",
                    className="lead", style={'margin-left': '10%', 'margin-right': '10%'}
                ),
            ],
            fluid=True,
            style={'max-height': '50px', 'min-height' : '10px', 'margin-top': '-5%'}
        )
    ],
    fluid=True,
))
])

app.layout = html.Div([

    header,
    dcc.Tabs(id='tabs', value='tab-1', children=[
    dcc.Tab(value='tab-2'),
 
    ]),
    html.Div(id='tabs-content-example')
])

# App callback for selecting the tabs
@app.callback(Output('tabs-content-example', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):

    return html.Div([
        dcc.Dropdown(
    id='dd-chart1',
    options=[
    {'label': 'Beauty Salon', 'value': 'Beauty Salon'},
    {'label': 'Dealer and Retailer', 'value': 'Dealer and Retailer'},
    {'label': 'Parkade', 'value': 'Parkade'},
    {'label': 'Contractor', 'value': 'Contractor'},
    {'label': 'Rental and Booking Agency', 'value': 'Rental and Booking Agency'},
    {'label': 'Car Services', 'value': 'Car Services'},
    {'label': 'Contractor and Freelancer', 'value': 'Contractor and Freelancer'},
    {'label': 'Resutaurant', 'value': 'Resutaurant'},
    {'label': 'Rental Management services', 'value': 'Rental Management services'},
    {'label': 'liquor and Adult store', 'value': 'liquor and Adult store'},
    {'label': 'Dwelling Office', 'value': 'Dwelling Office'},
    {'label': 'Food Retailer', 'value': 'Food Retailer'},
    ],
    value='Beauty Salon',
    style={ 'margin-left': '10%', 'width' : '45%', 'verticalAlign' : 'middle'}
            ),

    html.Iframe(
            sandbox='allow-scripts',
            id='plot1',
            height='600',
            width='1700',
                
            style={'border-width': '0', 'margin-left': '10%'},
            srcDoc = map().to_html()
            ),
                    
    ], )
    

# app callback for selecting the jobs from the dropdown menu
@app.callback(
dash.dependencies.Output('plot1', 'srcDoc'),
[dash.dependencies.Input('dd-chart1', 'value')])

# selecting the job and call the trend function
def select_business(business):
    '''
    Takes a Business type selected using the dropdown menu and updates the map plot accordingly

    parameters
    ------------------
    business : (str)
            business type

    returns 
    --------------------
    altair plot
    '''
    updated_plot = map(business_to_choose = business).to_html()
    return updated_plot

    
if __name__ == '__main__':
    app.run_server(debug=True)