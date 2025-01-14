import streamlit as st
import plotly.graph_objects as go
import numpy as np
from scipy.optimize import minimize_scalar

# Function to calculate total distance
def calculate_distance(bridge_x, A_x, A_y, B_x, B_y, river_width):
    bridge_y1, bridge_y2 = 0, river_width
    dist_A_to_bridge = np.sqrt((A_x - bridge_x) ** 2 + (A_y - bridge_y1) ** 2)
    dist_bridge_to_B = np.sqrt((B_x - bridge_x) ** 2 + (B_y - bridge_y2) ** 2)
    total_distance = dist_A_to_bridge + river_width + dist_bridge_to_B
    return dist_A_to_bridge, dist_bridge_to_B, total_distance

# Generate smooth data for distance curve
def generate_distance_curve(A_x, A_y, B_x, B_y, river_width):
    x_vals = np.linspace(0, 6, 500)
    y_vals = [calculate_distance(x, A_x, A_y, B_x, B_y, river_width)[2] for x in x_vals]
    return x_vals, y_vals

# Streamlit app
st.set_page_config(page_title="Bridge Optimization Simulator", layout="wide")

st.title("Bridge Optimization Simulator")
st.sidebar.header("Inputs")

# Input fields
A_x = st.sidebar.number_input("City A X-coordinate", value=0.0, step=0.1)
A_y = st.sidebar.number_input("City A Y-coordinate", value=-3.0, step=0.1)
B_x = st.sidebar.number_input("City B X-coordinate", value=6.0, step=0.1)
B_y = st.sidebar.number_input("City B Y-coordinate", value=6.0, step=0.1)
river_width = st.sidebar.slider("River Width (km)", min_value=0.5, max_value=3.0, value=1.0, step=0.1)
bridge_x = st.sidebar.slider("Bridge X-coordinate", min_value=0.0, max_value=6.0, value=3.0, step=0.01)

# Calculate distances and optimum position
dist_A_to_bridge, dist_bridge_to_B, total_distance = calculate_distance(bridge_x, A_x, A_y, B_x, B_y, river_width)
result = minimize_scalar(lambda x: calculate_distance(x, A_x, A_y, B_x, B_y, river_width)[2], bounds=(0, 6), method='bounded')
optimum_bridge_x = result.x
optimum_total_distance = result.fun

# Generate smooth data for distance curve
x_vals, y_vals = generate_distance_curve(A_x, A_y, B_x, B_y, river_width)

# Plot the graph
fig = go.Figure()

# Add river
fig.add_shape(type="rect", x0=-1, x1=7, y0=0, y1=river_width, fillcolor="lightblue", opacity=0.5, line_width=0)

# Add cities
fig.add_trace(go.Scatter(x=[A_x], y=[A_y], mode='markers', name='City A', marker=dict(size=12, color='red')))
fig.add_trace(go.Scatter(x=[B_x], y=[B_y], mode='markers', name='City B', marker=dict(size=12, color='green')))

# Add bridge
fig.add_trace(go.Scatter(x=[bridge_x, bridge_x], y=[0, river_width], mode='lines', name='Bridge',
                         line=dict(color='brown', width=4)))

# Add paths
fig.add_trace(go.Scatter(x=[A_x, bridge_x], y=[A_y, 0], mode='lines+markers', name='Path A → Bridge',
                         line=dict(color='orange', dash='dash')))
fig.add_trace(go.Scatter(x=[bridge_x, B_x], y=[river_width, B_y], mode='lines+markers', name='Path Bridge → B',
                         line=dict(color='purple', dash='dash')))

# Add annotations for distances
fig.add_annotation(x=(A_x + bridge_x) / 2, y=(A_y + 0) / 2, text=f"{dist_A_to_bridge:.4f} km",
                   showarrow=False, font=dict(color="orange", size=12))
fig.add_annotation(x=(bridge_x + B_x) / 2, y=(river_width + B_y) / 2, text=f"{dist_bridge_to_B:.4f} km",
                   showarrow=False, font=dict(color="purple", size=12))

# Add optimum placement
fig.add_trace(go.Scatter(x=[optimum_bridge_x], y=[river_width / 2], mode='markers+text',
                         name='Optimum Bridge', text=f"Optimum\n{optimum_bridge_x:.4f} km",
                         textposition='bottom center', marker=dict(size=10, color='blue')))
fig.add_trace(go.Scatter(x=[optimum_bridge_x, optimum_bridge_x], y=[0, river_width], mode='lines',
                         name='Optimum Bridge Position', line=dict(color='blue', dash='dot', width=2)))

# Add distance curve
fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name='Distance Curve', line=dict(color='green', width=2)))

# Update layout
fig.update_layout(
    xaxis=dict(range=[-1, 7], title="X Coordinate (km)"),
    yaxis=dict(range=[-4, 8], title="Y Coordinate (km)"),
    showlegend=True,
    title="Bridge Placement and Travel Path"
)

# Show plot and distances
st.plotly_chart(fig, use_container_width=True)
st.markdown(f"### Distance Metrics:")
st.markdown(f"**Current Distance**: {total_distance:.4f} km")
st.markdown(f"**A → Bridge**: {dist_A_to_bridge:.4f} km")
st.markdown(f"**Bridge → B**: {dist_bridge_to_B:.4f} km")
st.markdown(f"**Optimum Bridge Position**: {optimum_bridge_x:.4f} km")
st.markdown(f"**Optimum Total Distance**: {optimum_total_distance:.4f} km")
