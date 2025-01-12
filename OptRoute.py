import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np
from scipy.optimize import minimize_scalar

# App setup
app = dash.Dash(__name__)
app.title = "Bridge Optimization Simulator"

# Default values for city locations
default_A_x, default_A_y = 0, -3
default_B_x, default_B_y = 6, 6
river_width = 1

# Function to calculate total distance
def calculate_distance(bridge_x, A_x, A_y, B_x, B_y):
    bridge_y1, bridge_y2 = 0, river_width
    dist_A_to_bridge = np.sqrt((A_x - bridge_x) ** 2 + (A_y - bridge_y1) ** 2)
    dist_bridge_to_B = np.sqrt((B_x - bridge_x) ** 2 + (B_y - bridge_y2) ** 2)
    total_distance = dist_A_to_bridge + river_width + dist_bridge_to_B
    return total_distance

# Generate smooth data for distance curve
def generate_distance_curve(A_x, A_y, B_x, B_y):
    x_vals = np.linspace(0, 6, 500)
    y_vals = [calculate_distance(x, A_x, A_y, B_x, B_y) for x in x_vals]
    return x_vals, y_vals

# Layout
app.layout = html.Div([
    html.H1("Bridge Optimization Simulator", style={'textAlign': 'center'}),
    dcc.Graph(id='simulator-graph', style={'height': '70vh'}),
    
    html.Div([
        html.Label("City A Coordinates (x, y):"),
        dcc.Input(id="input-A-x", type="number", value=default_A_x, debounce=True, placeholder="x-coordinate of City A"),
        dcc.Input(id="input-A-y", type="number", value=default_A_y, debounce=True, placeholder="y-coordinate of City A"),
    ], style={'margin': '20px'}),
    
    html.Div([
        html.Label("City B Coordinates (x, y):"),
        dcc.Input(id="input-B-x", type="number", value=default_B_x, debounce=True, placeholder="x-coordinate of City B"),
        dcc.Input(id="input-B-y", type="number", value=default_B_y, debounce=True, placeholder="y-coordinate of City B"),
    ], style={'margin': '20px'}),
    
    html.Div([
        html.Label("Bridge Position (X-coordinate):"),
        dcc.Slider(
            id='bridge-slider',
            min=0,
            max=6,
            step=0.01,  # Increased precision
            value=3,
            marks={i: str(i) for i in range(7)},
        )
    ], style={'margin': '20px'}),
    
    html.Div(id='distance-output', style={'textAlign': 'center', 'marginTop': '10px', 'fontSize': '20px'})
])

# Callback for updating the graph and distance
@app.callback(
    [Output('simulator-graph', 'figure'),
     Output('distance-output', 'children')],
    [Input('bridge-slider', 'value'),
     Input('input-A-x', 'value'),
     Input('input-A-y', 'value'),
     Input('input-B-x', 'value'),
     Input('input-B-y', 'value')]
)
def update_graph(bridge_x, A_x, A_y, B_x, B_y):
    # Ensure the input values are numbers
    try:
        A_x = float(A_x)
        A_y = float(A_y)
        B_x = float(B_x)
        B_y = float(B_y)
    except ValueError:
        return go.Figure(), "Invalid coordinates. Please input valid numbers for cities A and B."
    
    # Calculate optimum bridge position for current A and B
    result = minimize_scalar(calculate_distance, bounds=(0, 6), args=(A_x, A_y, B_x, B_y), method='bounded')
    optimum_bridge_x = result.x
    optimum_distance = result.fun

    # Generate smooth data for distance curve
    x_vals, y_vals = generate_distance_curve(A_x, A_y, B_x, B_y)

    # Calculate distances for current slider value
    total_distance = calculate_distance(bridge_x, A_x, A_y, B_x, B_y)
    dist_A_to_bridge = np.sqrt((A_x - bridge_x) ** 2 + (A_y - 0) ** 2)
    dist_bridge_to_B = np.sqrt((B_x - bridge_x) ** 2 + (B_y - river_width) ** 2)

    # Create the plot
    fig = go.Figure()
    # Add river
    fig.add_shape(type="rect", x0=-1, x1=7, y0=0, y1=river_width,
                  fillcolor="lightblue", opacity=0.5, line_width=0)
    # Add cities
    fig.add_trace(go.Scatter(x=[A_x], y=[A_y], mode='markers', name='City A',
                             marker=dict(size=12, color='red')))
    fig.add_trace(go.Scatter(x=[B_x], y=[B_y], mode='markers', name='City B',
                             marker=dict(size=12, color='green')))
    # Add bridge
    fig.add_trace(go.Scatter(x=[bridge_x, bridge_x], y=[0, river_width],
                             mode='lines', name='Bridge (Draggable)',
                             line=dict(color='brown', width=4)))
    # Add paths
    fig.add_trace(go.Scatter(x=[A_x, bridge_x], y=[A_y, 0],
                             mode='lines', name='Path A to Bridge',
                             line=dict(color='orange', dash='dash')))
    fig.add_trace(go.Scatter(x=[bridge_x, B_x], y=[river_width, B_y],
                             mode='lines', name='Path Bridge to B',
                             line=dict(color='purple', dash='dash')))
    # Add optimum line
    fig.add_trace(go.Scatter(x=[optimum_bridge_x, optimum_bridge_x], y=[0, river_width],
                             mode='lines', name='Optimum Bridge Position',
                             line=dict(color='blue', dash='dot', width=2)))
    # Add optimum label
    fig.add_trace(go.Scatter(x=[optimum_bridge_x], y=[river_width],
                             mode='markers+text', text=f"Optimum: {optimum_bridge_x:.4f} km",
                             textposition="top center", marker=dict(color='blue', size=10)))
    # Add distance curve
    fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name='Distance Curve',
                             line=dict(color='green', width=2)))

    # Set layout
    fig.update_layout(
        xaxis=dict(range=[-1, 7], title="X Coordinate (km)"),
        yaxis=dict(range=[-4, 8], title="Y Coordinate (km)"),
        showlegend=True,
        title="Bridge Placement and Travel Path"
    )

    # Update distance text with higher precision
    distance_text = (f"Current Distance: {total_distance:.4f} km | "
                     f"Optimum Distance: {optimum_distance:.4f} km | "
                     f"A to Bridge: {dist_A_to_bridge:.4f} km | "
                     f"Bridge to B: {dist_bridge_to_B:.4f} km")
    return fig, distance_text

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
