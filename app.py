from dash import Dash, dcc, html, Input, Output, State, dash_table, callback
import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go  # Import for custom modifications
from dash.dependencies import Input, Output, ClientsideFunction
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import json


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='resizeTextarea'
    ),
    Output('incentive-text-dummy-output', 'children'),  # Dummy output, not used
    [Input('incentive-text', 'value')]
)

accepted_emails = [
    'payton@ecsempire.com',
    'wayne@ecsempire.com',
    'robert@ecsempire.com',
    'george@ecsempire.com',
    'justin@ecsempire.com',
    'keenan@ecsempire.com',
    'taylor@ecsempire.com'
]

# Prepare the data
names = ["Rob", "Wayne", "George", "JT", "Keenan", "Payton", "Taylor"]
weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]



# Create a DataFrame with placeholders for sales data
data = pd.DataFrame(index=names, columns=weekdays).reset_index().rename(columns={'index': 'Name'})
data.fillna(0, inplace=True)  # Replace NaN with 0 for editable purposes

data['Goal'] = 1000

def load_data_from_json(filename='sales_data.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []  # Return an empty list if no data file exists

def save_data_to_json(data, filename='sales_data.json'):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        print("data saved successfully")
    except Exception as e:
        print(f"error saving data: {e}")


# Define initial bar graph figure
initial_fig = go.Figure()

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='user-access-level'),  # Store the user's access level
    html.Div(id='page-content')
])

index_page = html.Div([
    html.Div([  # Add an inner div to specifically center the login elements
        dcc.Input(
            id='email-input',
            type='email',
            placeholder='Enter your email',
            style={
                'margin': '10px auto',  # Center horizontally
                'width': '40%',  
                'padding': '15px',  
                'fontSize': '18px',
                'display': 'block'  # Ensure the input behaves as a block element for margin auto to work
            }
        ),
        html.Button(
            'Login',
            id='login-button',
            n_clicks=0,
            style={
                'margin': '10px auto',  # Center horizontally
                'width': '40%',  
                'padding': '15px',  
                'fontSize': '18px',
                'cursor': 'pointer',
                'display': 'block'  # Ensure the button behaves as a block element for margin auto to work
            }
        ),
        html.Div(id='login-feedback')
    ], style={'width': '100%', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),  # This centers the content vertically
], style={'textAlign': 'center', 'backgroundColor': '#990000', 'height': '100vh', 'display': 'flex', 'justifyContent': 'center', 'flexDirection': 'column'})

@app.callback(
    [Output('url', 'pathname'),
     Output('user-access-level', 'data')],  # Store data in dcc.Store
    Input('login-button', 'n_clicks'),
    State('email-input', 'value')
)
def update_output(n_clicks, email):
    if n_clicks > 0:
        if email in accepted_emails:
            access_level = 'full' if email in ['payton@ecsempire.com', 'wayne@ecsempire.com', 'robert@ecsempire.com'] else 'limited'
        return '/page_1', {'access': access_level}  # This is the URL path you want to redirect to
    return '/', {}  # Stay on the index page if conditions are not met

@app.callback(
    [Output('sales-table', 'disabled'),
     Output('incentive-text', 'disabled'),
     # Add more Outputs as necessary for each editable component
    ],
    [Input('user-access-level', 'data')]
)
def adjust_editable_cells(access_data):
    if access_data and access_data.get('access') == 'full':
        # If access level is full, enable the components (set disabled to False)
        return (False, False)  # Repeat False for as many components as you have
    # If access level is not full, disable the components (set disabled to True)
    return (True, True)  # Repeat True for as many components as you have


page_1_layout = html.Div(children=[
    # Parent div for logos and title
    html.Div(children=[
        # Left logo
        html.Img(src='/assets/ECS TRANSPARENT LOGO.png', style={'height': '200px', 'width': 'auto', 'display': 'inline-block'}),
        
        # Title
        html.H1(children='Empire Sales Board', style={
            'font-family': 'Impact, Charcoal, sans-serif',
            'color': '#FFFFFF',
            'textAlign': 'center',
            'display': 'inline-block',
            'margin': '0 20px',
            'font-size': '72px'  # Adjusted font size
        }),
        
        # Right logo
        html.Img(src='/assets/ECS TRANSPARENT LOGO.png', style={'height': '200px', 'width': 'auto', 'display': 'inline-block'}),
    ], style={'textAlign': 'center', 'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}),
    
    # Sales table
    
    dash_table.DataTable(
        id='sales-table',
        columns=(
            [{"name": "Name", "id": "Name", "editable": False}] +  # Make Name column non-editable
            [{"name": day, "id": day, "editable":True} for day in weekdays] +  # Make weekday columns editable
            [{"name": "Goal", "id": "Goal", "editable": True}]  # Add editable Goal column
        ),
        data=load_data_from_json(),  # Load the data directly here
        editable=True,
          # Allow editing, controlled at the column level
        style_table={'height': '300px', 'overflowY': 'auto'},
        style_cell={
            'textAlign': 'left',
            'border': '5px solid maroon',
            'padding': '5px',
        },
        style_data_conditional=[
            {'if': {'filter_query': '{{{}}} <= 1000'.format(col), 'column_id': col},
             'color': 'black'} for col in weekdays
        ] + [
            {'if': {'filter_query': '1000 < {{{}}} <= 2000'.format(col), 'column_id': col},
             'color': 'red'} for col in weekdays
        ] + [
            {'if': {'filter_query': '2000 < {{{}}} <= 3000'.format(col), 'column_id': col},
             'color': 'blue'} for col in weekdays
        ] + [
            {'if': {'filter_query': '3000 < {{{}}} <= 4000'.format(col), 'column_id': col},
             'color': 'green'} for col in weekdays
        ] + [
            {'if': {'filter_query': '4000 < {{{}}} <= 5000'.format(col), 'column_id': col},
             'color': 'purple'} for col in weekdays
        ] + [
            {'if': {'filter_query': '{{{}}} > 5000'.format(col), 'column_id': col},
             'color': 'orange'} for col in weekdays
        ]
    ),
 html.Div(id='save-status', style={'color': 'green', 'margin': '10px', 'textAlign': 'center'}),
 html.Div([
        dcc.Textarea(
            id='incentive-text',
            value='Everyone needs more blades...',
            style={
                'width': '100%', 
                'height': 'auto', 
                'minHeight': '50px', 
                'backgroundColor': 'rgba(255, 120, 0, 0.65)',
                'fontSize': '20px',
                'textAlign': 'center',
                'color': '#000000',
                'font-family': 'Impact, Charcoal, sans-serif',
            }
        ),
        html.Div(id='incentive-text-dummy-output', style={'display': 'none'})
    ], style={'margin': '0px 0'}),

    # Container for the graph to adjust width without affecting the background
    html.Div([
        # Left Column for the Graph
        html.Div([
            dcc.Graph(
                id='sales-graph',
                # figure=figure  # Your Plotly figure goes here
            )
        ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        # Right Column for the Cycling Image
        html.Div([
            html.Img(id='cycling-image', src='/assets/WOC_deals1.jpg', style={'width': '100%', 'height': '400px'}),
        ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ], style={'display': 'flex', 'width': '100%'}),
    
    # Interval component for triggering updates to the image
    dcc.Interval(
        id='interval-component',
        interval=10*1000,  # in milliseconds, e.g., 5 seconds
        n_intervals=0
    ),

], style={
    'backgroundImage': 'url("/assets/hex_bg_red.gif")',
    'backgroundRepeat': 'repeat',
    'backgroundPosition': 'center',
    'backgroundSize': 'cover',
    'height': '100%',  # Adjusting to '100vh' for full viewport height coverage
    'width': '100%'
})  

@app.callback(
    Output('sales-table', 'data'),  # Assuming 'sales-table' is the id of your DataTable
    [Input('url', 'pathname')]
)
def load_data_on_page_load_or_refresh(pathname):
    data = load_data_from_json()  # Your function to load data from JSON
    return data
# Assuming `app` is your Dash app instance and `data` is the DataFrame

@app.callback(
    Output('save-status', 'children'),  # Replace with an actual Output if needed
    Input('sales-table', 'data_timestamp'),
    State('sales-table', 'data'),
    prevent_initial_call=True
)
def save_table_on_edit(timestamp, data):
    if data:
        save_data_to_json(data)
        return "Data saved!"  # Or another suitable message/action  
    return "no data to save"  # Or another suitable message/action

@app.callback(
    Output('cycling-image', 'src'),
    [Input('interval-component', 'n_intervals')]
)
def update_image(n_intervals):
    # List of images to cycle through
    images = ['/assets/WOC_deals1.jpg', '/assets/WOC_deals2.jpg']
    # Select the image based on the current interval
    current_image = images[n_intervals % len(images)]
    return current_image


# Callback to update the graph based on table data
@app.callback(
    Output('sales-graph', 'figure'),
    [Input('sales-table', 'data')]
)
def update_graph(rows):
    # Convert table rows to DataFrame
    df = pd.DataFrame(rows)

    # Ensure data is numeric
    for col in weekdays:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Calculate total sales for each person and overall total
    df['Total'] = df[weekdays].sum(axis=1)
    total_sales = df['Total'].sum()
    
    # Append total sales as a separate row for visualization
    df = df.append({'Name': 'Total Sales', 'Total': total_sales}, ignore_index=True)

    # Define color based on sales thresholds
    colors = df['Total'].apply(lambda x: 
                               'black' if x <= 1000 else
                               'red' if 1000 < x <= 2000 else
                               'blue' if 2000 < x <= 3000 else
                               'green' if 3000 < x <= 4000 else
                               'purple' if 4000 < x <= 5000 else
                               'orange')
    
    # Create the bar graph with conditional colors
    fig = go.Figure(data=[
        go.Bar(
            y=df['Name'],
            x=df['Total'],
            orientation='h',
            marker_color=colors,  # Apply conditional colors
            text=df['Total'],
            textposition='auto',
        )
    ])

    # Update graph layout to center the title and match the app's background color
    fig.update_layout(
        title_text='Sales',
        title_x=0.5,  # Center the title
        title_font=dict(size=24,family='Impact, Charcoal, sans-serif'),  # Adjust the title font size here
        yaxis={'categoryorder': 'total ascending'},
        paper_bgcolor='rgba(0, 0, 0, 0)',  # Match the app's background color
        font_color='#FFFFFF',
        plot_bgcolor= 'rgba(0, 0, 0, 0)'  # Improve text contrast against the dark background
    )

    return fig

# Callback to render page content based on URL
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page_1':
        return page_1_layout
    else:
        return index_page  # Or any other default page you have



page_2_layout = html.Div([
    html.H1('Page 2'),
    dcc.RadioItems(['Orange', 'Blue', 'Red'], 'Orange', id='page-2-radios'),
    html.Div(id='page-2-content'),
    html.Br(),
    dcc.Link('Go to Page 1', href='/page-1'),
    html.Br(),
    dcc.Link('Go back to home', href='/')
])


@callback(Output('page-2-content', 'children'), Input('page-2-radios', 'value'))
def page_2_radios(value):
    return f'You have selected {value}'


# Update the index
@callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/page-1':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    else:
        return index_page
    # You could also return a 404 "URL not found" page here


if __name__ == '__main__':
    app.run(debug=True)