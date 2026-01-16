import plotly.graph_objects as go
import urllib.request
import urllib.parse
import json

def get_planet_coords(target, center, start='1999-10-15', stop='2083-10-15', step='1d'):
    """
    Fetch planetary coordinates from NASA Horizons API
    
    Args:
        target: Planet ID (e.g., '399' for Earth)
        center: Center point (default: '10' = Sun)
        start: Start date (YYYY-MM-DD)
        stop: End date (YYYY-MM-DD)
        step: Time step (e.g., '30d' = 30 days)
    
    Returns:
        List of [x, y, z] coordinates in AU
    """
    API_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
    
    params = {
        "format": "json",
        "COMMAND": target,
        "CENTER": center,
        "MAKE_EPHEM": "YES",
        "EPHEM_TYPE": "VECTORS",
        "OUT_UNITS": "AU-D",
        "START_TIME": start,
        "STOP_TIME": stop,
        "STEP_SIZE": step
    }
    # get data from nasa
    query = urllib.parse.urlencode(params)
    url = f"{API_URL}?{query}"
    
    with urllib.request.urlopen(url) as response:
        data = response.read().decode("utf-8")
        result = json.loads(data)
    
    # Parse coordinates from the result
    coords = []
    data_section = result["result"].split("$$SOE")[1].split("$$EOE")[0]
    lines = [line.strip() for line in data_section.strip().splitlines() if line.strip()]
    
    for i in range(0, len(lines), 4):
        pos_line = lines[i+1]
        x_str = pos_line.split("X =")[1].split("Y =")[0].strip()
        y_str = pos_line.split("Y =")[1].split("Z =")[0].strip()
        z_str = pos_line.split("Z =")[1].strip()
        coords.append([float(x_str), float(y_str), float(z_str)])
    
    return coords

# Define planets to visualize
planets = [
    {'id': '10', 'name': 'Sun', 'color': 'yellow'},
    {'id': '301', 'name': 'Moon', 'color': 'purple'},
    {'id': '199', 'name': 'Mercury', 'color': 'orange'},
    {'id': '299', 'name': 'Venus', 'color': 'green'},
    {'id': '399', 'name': 'Earth', 'color': 'blue'},
    {'id': '499', 'name': 'Mars', 'color': 'red'},
    {'id': '599', 'name': 'Jupiter', 'color': 'blue'},
    {'id': '699', 'name': 'Saturn', "color": 'black'}
]

def visualize_orbits(planets_config, center_index, title="Geocentric Solar System"):
    """
    Create interactive 3D visualization of planetary orbits from a geocentric perspective
    
    :param planets_config: List of dicts with 'id', 'name', and 'color' keys
    :param center_index: the index of the list of planets that will be used as the reference point for the orbit gen
    :param title: Geocentric Solar System
    """
    fig = go.Figure()

    #gets info on the center planet, easier to read :^)
    center_planet_id = planets_config[center_index]['id']
    center_name = planets_config[center_index]['name']
    center_color = planets_config[center_index]['color']

    # Fetch and plot each planet's orbit
    for i, planet in enumerate(planets_config):
        if i != center_index:
            print(f"Fetching {planet['name']} relative to {center_name}...")
            coords = get_planet_coords(planet['id'], center_planet_id)
            x, y, z = zip(*coords)

            fig.add_trace(go.Scatter3d(
                x=x, y=y, z=z,
                mode='lines',
                line=dict(color=planet['color'], width=1),
                name=planet['name']
            ))
        else:
            # center planet is in the center, no need for pulling coordinates
            fig.add_trace(go.Scatter3d(
                x=[0], y=[0], z=[0],
                mode='markers',
                marker=dict(color=center_color, size=1),
                name=center_name
            ))

    # Update layout
    fig.update_layout(
        title={
            'text': title,
            'x': 0.25,
            'xanchor': 'center'
    }   ,
        annotations=[
            dict(
                text="Plotted over 83 years<br><sub>Data from NASA Jet Propulsion Labratory",
                xref="paper", yref="paper",
                x=0.2, y=1.1,
                showarrow=False,
                xanchor='center',
                font=dict(size=12, color="gray")
            )
        ],
        scene=dict(
            xaxis_title='X (AU)',
            yaxis_title='Y (AU)',
            zaxis_title='Z (AU)',
            aspectmode='data',
            camera=dict(
                eye=dict(x=0, y=0, z=2),
                center=dict(x=0, y=0, z=0),
                up=dict(x=0, y=1, z=0)
            )
        ),
        showlegend=True,
        margin=dict(l=100, r=100, t=150, b=0)
        )
    
    return fig

# visual for multiple center points (WIP)
def create_multi_center_visualization(planets_config, center_indices=[0, 4]):
    """
    Create visualization with buttons to switch between different center perspectives
    
    Args:
        planets_config: List of planet dictionaries
        center_indices: List of indices to create views for (e.g., [0, 4] for Sun and Earth)
    """
    fig = go.Figure()

    coords_by_center = {}
    for center_idx in center_indices:
        center_id = planets_config[center_idx]["id"]
        coords_by_center

    # Traces for perspective selector
    trace_groups = []
    
    for view_idx, center_idx in enumerate(center_indices):
        center_planet_id = planets_config[center_idx]['id']
        center_name = planets_config[center_idx]['name']
        center_color = planets_config[center_idx]['color']

        group_traces = []

        print(f"/nGenerating {center_name}-centric view...")

        for i, planet in enumerate(planets_config):
            if i != center_idx:
                print(f"    Fetching {planet['name']} relative to {center_name}...")
                coords = get_planet_coords(planet['id'], center_planet_id)
                x, y, z = zip(*coords)
                trace = go.Scatter3d(
                    x=x, y=y, z=z,
                    mode='lines',
                    line=dict(color=planet['color'], width=3),
                    name=planet['name'],
                    visible=True
                )
                fig.add_trace(trace)
                group_traces.append(len(fig.data) - 1)
            else:
                trace = go.Scatter3d(
                    x=[0], y=[0], z=[0],
                    mode='markers',
                    marker=dict(color=center_color, size=10),
                    name=center_name,
                    visible=True
                )
                fig.add_trace(trace)
                group_traces.append(len(fig.data) - 1)
        
        trace_groups.append(group_traces)
    
    # make buttons that switch the views
    buttons = []
    for view_idx, center_idx in enumerate(center_indices):
        
        # Create visibility list: all False, then True for this view's traces
        visible = [False] * len(fig.data)
        for trace_idx in trace_groups[view_idx]:
            visible[trace_idx] = True

        button = dict(
            label=f"{planets_config[center_idx]['name']}-centric",
            method="restyle",
            args=[
                {"visible": visible},
                {"title": f"{planets_config[center_idx]['name']}-centric Solar System"}
            ]
        )
        buttons.append(button)
    
    fig.update_layout(
        title={
            'text': f"{planets_config[center_indices[0]]['name']}-centric Solar System",
            'x': 0.25,
            'xanchor': 'center'
        },
        annotations=[
            dict(
                text="Plotted over 83 years<br><sub>Data from NASA Jet Propulsion Laboratory",
                xref="paper", yref="paper",
                x=0.2, y=1.1,
                showarrow=False,
                xanchor='center',
                font=dict(size=12, color="gray")
            )
        ],
        scene=dict(
            xaxis_title='X (AU)',
            yaxis_title='Y (AU)',
            zaxis_title='Z (AU)',
            aspectmode='data',
            camera=dict(
                eye=dict(x=0, y=0, z=2),
                center=dict(x=0, y=0, z=0),
                up=dict(x=0, y=1, z=0)
            )
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=buttons,
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.0,
                xanchor="left",
                y=1.15,
                yanchor="top"
            )
        ],
        showlegend=True,
        margin=dict(l=100, r=100, t=150, b=0)
    )
    
    return fig


# Create visualization
print("Creating orbital visualization...")
fig = visualize_orbits(planets, 4)

# Show interactive plot
fig.show()

# Save to HTML file
output_file = "Orbigen.html"
fig.write_html(output_file)
print(f"\nVisualization saved to {output_file}")