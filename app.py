from dash import Dash, dcc, html, Input, Output, State, dash_table, callback, callback_context
import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go  # Import for custom modifications
from dash.dependencies import Input, Output, ClientsideFunction
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import json
from datetime import datetime, timedelta


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
    'taylor@ecsempire.com',
    'josh@ecsempire.com',
    'daniel@ecsempire.com',
    'andrew@ecsempire.com'
]

# Prepare the data
names = ["Rob", "Wayne", "George", "JT", "Keenan",  "Josh", "Daniel", "Andrew"]
weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]



# Create a DataFrame with placeholders for sales data
data = pd.DataFrame(index=names, columns=weekdays).reset_index().rename(columns={'index': 'Name'})
data.fillna(0, inplace=True)  # Replace NaN with 0 for editable purposes

data['Total'] = data[weekdays].sum(axis=1)

def load_data_from_json(filename='sales_data.json'):
    try:
        with open(filename, 'r') as file:
            data_dict = json.load(file)
        # Convert the loaded data into a DataFrame
        df = pd.DataFrame(data_dict)
        # Ensure all weekday columns are numeric and replace any NaNs with 0
        for day in weekdays:
            df[day] = pd.to_numeric(df[day], errors='coerce').fillna(0)
        # Calculate the 'Total' column after ensuring numeric conversion
        df['Total'] = df[weekdays].sum(axis=1)
        return df.to_dict('records')  # Convert DataFrame back to dict format for DataTable
    except FileNotFoundError:
        return []  # Return an empty list if no data file exists

def save_data_to_json(data, filename='sales_data.json'):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        print("data saved successfully")
    except Exception as e:
        print(f"error saving data: {e}")

def save_incentive_text_to_json(text, filename='incentive_data.json'):
    try:
        data = {'incentive_text': text}
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        return "Incentive text saved successfully."
    except Exception as e:
        return f"Error saving incentive text: {e}"

def load_incentive_text_from_json(filename='incentive_data.json'):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            return data.get('incentive_text', '')  # Return empty string if not found
    except FileNotFoundError:
        return ""  # Return empty string if file doesn't exist
    except Exception as e:
        return f"Error loading incentive text: {e}"



# Define initial bar graph figure
initial_fig = go.Figure()

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='notification-data', data=json.dumps({'last_data': None, 'show_notification': False})),
    dcc.Store(id='user-access-level'),  # Store the user's access level
    html.Div(id='page-content'),
    html.Audio(id='notification-audio', src='/assets/Explosion.mp3', autoPlay=True, style={'display': 'none'})
       



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
    State('email-input', 'value'),
)
def update_output(n_clicks, email):
    if n_clicks > 0:
        if email in accepted_emails:
            access_level = 'full' if email in ['payton@ecsempire.com', 'wayne@ecsempire.com', 'robert@ecsempire.com', 'george@ecsempire.com'] else 'limited'
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
    
    
    html.Div([

        

    
        dash_table.DataTable(
            id='sales-table',
            columns=(
                [{"name": "Name", "id": "Name", "editable": False}] +  # Make Name column non-editable
                [{"name": day, "id": day, "editable":True} for day in weekdays] +  # Make weekday columns editable
                [{"name": "Total", "id": "Total", "editable": False}]  # Add non-editable Total column
            ),
            data=load_data_from_json(),  # Load the data directly here
            editable=True,
            # Allow editing, controlled at the column level
            style_table={'height': '645px', 'overflowY': 'auto'},
            style_cell={
            'textAlign': 'center',
            'border': '5px solid maroon',
            'padding': '5px',
            'fontSize': '42px',
            'fontFamily': 'Impact',
            'height': '65px',  # Increase cell height
            'backgroundColor': 'rgba(255, 255, 255, 0.5)',
            'whiteSpace': 'normal',  # Ensures text wrapping is enabled
            'minWidth': '180px',  # Adjust as needed
            'width': '180px',  # Adjust as needed
            'maxWidth': '180px',  # Adjust as needed
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            },
            style_data_conditional=[
                {'if': {'filter_query': '{{{}}} <= 999'.format(col), 'column_id': col},
                'color': 'black'} for col in weekdays
            ] + [
                {'if': {'filter_query': '999 < {{{}}} <= 1999'.format(col), 'column_id': col},
                'color': 'red'} for col in weekdays
            ] + [
                {'if': {'filter_query': '1999 < {{{}}} <= 2999'.format(col), 'column_id': col},
                'color': 'blue'} for col in weekdays
            ] + [
                {'if': {'filter_query': '2999 < {{{}}} <= 3999'.format(col), 'column_id': col},
                'color': 'orange'} for col in weekdays
            ] + [
                {'if': {'filter_query': '3999 < {{{}}} <= 4999'.format(col), 'column_id': col},
                'color': 'purple'} for col in weekdays
            ] + [
                {'if': {'filter_query': '{{{}}} > 4999'.format(col), 'column_id': col},
                'color': 'green'} for col in weekdays
            ], 
        

    ),
     html.Div(id='incentive-text-save-status', style={'display': 'none','color': 'green', 'textAlign': 'center'}),
     html.Div(id='save-status', style={'display': 'none','color': 'green', 'textAlign': 'center'}),
    html.Div([
        dcc.Textarea(
            id='incentive-text',
            value='Everyone needs more blades...',
            style={
                'width': '100%', 
                'height': 'auto', 
                'minHeight': '150px', 
                'backgroundColor': 'rgba(255, 120, 0, 0.65)',
                'fontSize': '70px',
                'textAlign': 'center',
                'color': '#000000',
                'font-family': 'Impact, Charcoal, sans-serif',
            }
        ),
        html.Div(id='incentive-text-dummy-output', style={'display': 'none'})
    ], style={'margin': '10px 0'}),
    html.Div(id='page-load-trigger', style={'display': 'none'}),

    # Container for the graph to adjust width without affecting the background
    html.Div([
        # Left Column for the Graph
        html.Div([
            dcc.Graph(
                id='sales-graph',
                # figure=figure  # Your Plotly figure goes here
            )
        ], style={'width': '100%', 'display': 'block', 'verticalAlign': 'top'}),  # Adjusted for clarity
    
    # Image Container
    html.Div([
        html.Img(
            id='cycling-image', 
            src='/assets/WOC_deals1.jpg', 
            style={
                'width': '100%',  # This ensures the image is responsive and fills the width of its container
                'height': 'auto',  # Setting height to auto preserves the image's aspect ratio
                'object-fit': 'contain',  # This makes sure the image is scaled to be as large as possible without cropping or stretching
                'display': 'block',  # Ensures the image is not inline
                'maxHeight': '400px',  # You can adjust this value to set a maximum height
            }
        ),
    ], style={'width': '100%', 'display': 'block', 'verticalAlign': 'top'}),
], style={'position': 'relative','display': 'flex', 'flex-direction': 'column', 'width': '100%'}),
    
    # Interval component for triggering updates to the image
    dcc.Interval(
        id='interval-component',
        interval=15*1000,  # in milliseconds,
        n_intervals=0
    ),

    html.Div(id='notification', style={'display': 'none',
                                       'position': 'fixed',
                                       'top': '20%', 
                                       'left': '50%', 
                                       'transform': 'translate(-50%, -50%)', 
                                       'zIndex': '9999', 
                                       'backgroundColor': 
                                       'rgba(0, 255, 0, 0.9)', 
                                       'padding': '20px', 
                                       'borderRadius': '10px', 
                                       'color': 'white', 
                                       'fontSize': '20px'}),

], style={
    'backgroundImage': 'url("/assets/hex_Backg.gif")',
    'backgroundRepeat': 'repeat',
    'backgroundPosition': 'center',
    'backgroundSize': 'cover',
    'height': '100%',  # Adjusting to '100vh' for full viewport height coverage
    'width': '100%'
})  

])

            # return {'display': 'block', 'position': 'fixed', 'top': '20%', 'left': '50%', 'transform': 'translate(-50%, -50%)', 'zIndex': '9999', 'backgroundColor': 'rgba(0, 255, 0, 0.9)', 'padding': '20px', 'borderRadius': '10px', 'color': 'white', 'fontSize': '20px'}, message, json.dumps(new_notification_data)

@app.callback(
    [Output('notification', 'style'),
     Output('notification', 'children'),
     Output('notification-data', 'data')],
    [Input('interval-component', 'n_intervals')],
    [State('sales-table', 'data'),
     State('notification-data', 'data')]
)
def manage_notification(n_intervals, current_rows, notification_data_json):
    notification_data = json.loads(notification_data_json)
    last_data = notification_data.get('last_data')
    show_notification = notification_data.get('show_notification')

    # Convert current rows to DataFrame for comparison
    current_df = pd.DataFrame(current_rows)
    
    # Initialize message
    message = ""

    # Determine if there's been a change in the "Total" column
    if last_data is not None:
        last_df = pd.DataFrame(last_data).set_index('Name')
        current_df = current_df.set_index('Name')

        # Check if the "Total" for any individual has increased by aligning both data frames on their index (Name)
        increased_totals = (current_df['Total'] > last_df['Total']).reindex_like(current_df)

        if increased_totals.any():
            # Find the names of individuals whose "Total" has increased
            names_with_increased_totals = increased_totals[increased_totals].index.tolist()
            # Create a message for the notification
            message = ", ".join(names_with_increased_totals) + " got a sale!!!"
            # Update to show notification
            show_notification = True
        else:
            # If there are no increases, do not show the notification
            show_notification = False
    else:
        # If last_data is None, it means it's the initial load, so we prevent showing the notification
        show_notification = False

    # Update the notification_data with the current state for comparison in the next call
    new_notification_data = json.dumps({'last_data': current_df.reset_index().to_dict('records'), 'show_notification': show_notification})

    if show_notification:
        # Display the notification
        return [{'display': 'block',
                 'position': 'fixed',
                 'top': '50%',
                 'left': '0',
                 'width': '100%',
                 'transform': 'translate(0, -50%)',
                 'zIndex': '9999',
                 'backgroundColor': 'rgba(0, 255, 0, 0.9)',
                 'padding': '20px',
                 'borderRadius': '10px',
                 'color': 'white',
                 'fontSize': '5em',
                 'font-family': 'Impact, Charcoal, sans-serif',
                 'textAlign': 'center'}, message, new_notification_data]
    else:
        # Hide the notification
        return [{'display': 'none'}, "", new_notification_data]

@app.callback(
    Output('notification-audio', 'src'),
    [Input('notification-data', 'data'),
     Input('url', 'pathname')],# Assuming this holds the condition for triggering the notification
    prevent_initial_call=True  # Prevents the audio from playing immediately when the app loads
)
def trigger_audio_playback(notification_data, pathname):
    notification_data = json.loads(notification_data)
    show_notification = notification_data.get('show_notification', False)

    if show_notification and pathname not in ['/', '/index_page']:
        # Specify the path to your audio file. If it's stored in the assets folder, it can be referenced directly.
        return app.get_asset_url('Explosion.mp3')
    else:
        # Return no audio if the condition to show notification is not met
        return ''
@app.callback(
    Output('incentive-text', 'value'),  # Assuming 'incentive-text' is the id of your Textarea
    [Input('interval-component', 'n_intervals')]  # Triggered by the Interval component
)
def refresh_incentive_text(n):
    if n % 2 == 0:  # Check if the interval count is even
        return load_incentive_text_from_json()  # Your function to load incentives from JSON
    raise dash.exceptions.PreventUpdate  # Prevents updating the component

@app.callback(
    Output('incentive-text-save-status', 'children'),  # An element to show save status
    Input('incentive-text', 'n_blur'),  # Triggered when user clicks outside the textarea
    State('incentive-text', 'value')  # Current value of the textarea
)
def save_incentive_text_on_edit(n_blur, text):
    if n_blur is not None and n_blur > 0:  # Check if there's been at least one blur event
        save_status = save_incentive_text_to_json(text)
        return save_status
    return "No changes detected"

@app.callback(
    Output('sales-table', 'data'),  # Assuming 'sales-table' is the id of your DataTable
    [Input('interval-component', 'n_intervals')]  # Triggered by the Interval component
)
def refresh_sales_data(n):
    return load_data_from_json()  # Your function to load data from JSON
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
                               'black' if x <= 999 else
                               'red' if 999 < x <= 1999 else
                               'blue' if 1999 < x <= 2999 else
                               'green' if 2999 < x <= 3999 else
                               'purple' if 3999 < x <= 4999 else
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
        plot_bgcolor= 'rgba(0, 0, 0, 0)',  # Improve text contrast against the dark background
        height=700
    )

    return fig

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input('user-access-level', 'data')])  # Consider user access level
def display_page(pathname, user_access_level):
    # Default to login page if no user access level data is available or for the root path
    if pathname == "/" or user_access_level is None:
        return index_page

    if pathname == '/page_1':
        # Here, you could further customize the response based on user access level
        if user_access_level.get('access') == 'full' or user_access_level.get('access') == 'limited':
            return page_1_layout
        else:
            # Redirect to login page if the access level is not recognized
            return index_page

    # Add conditions for other pages as necessary

    # Fallback for unrecognized paths
    return "Page not found"  # Consider a more user-friendly 404 page

if __name__ == '__main__':
    app.run(debug=True)
