"""
Author:
Abdul Sattar Sanny (202173944)
Abrar Faiyaz (201940046)

"""


import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import gaussian_kde

df_raw = pd.read_csv("satcat.tsv", sep="\t", low_memory=False)


def parse_vague_date(s):
    if pd.isna(s) or s.strip() in ("?", ""):
        return pd.NaT
    s = s.strip().rstrip("?s")
    for fmt in ["%Y %b %d %H%M", "%Y %b %d", "%Y %b", "%Y"]:
        try:
            return pd.to_datetime(s, format=fmt)
        except:
            continue
    return pd.NaT


df_raw["LDate"] = df_raw["LDate"].apply(parse_vague_date)
df_raw["DDate"] = df_raw["DDate"].apply(parse_vague_date)

df = df_raw[df_raw["Type"].str.startswith("P", na=False)].copy()
df["DecayOrNow"] = df["DDate"].fillna(pd.Timestamp.now())
df["Lifespan_Years"] = (df["DecayOrNow"] - df["LDate"]).dt.total_seconds() / (365.25 * 24 * 3600)
df = df[(df["Lifespan_Years"] >= 0) & (df["Lifespan_Years"] <= 100)]
df["Launch_Year"] = df["LDate"].dt.year
df["Launch_Decade"] = (df["Launch_Year"] // 10) * 10
df["IsActive"] = df["DDate"].isna()
df["Mass"] = pd.to_numeric(df["Mass"], errors='coerce')

orbit_map = {
    "LLEO/S": "LEO", "LLEO/I": "LEO", "LEO/S": "LEO", "LEO/I": "LEO", "LEO": "LEO", "SSO": "LEO",
    "GEO": "GEO", "GEO/I": "GEO", "GEO/S": "GEO",
    "MEO": "MEO", "MEO/I": "MEO",
    "HEO": "HEO", "HEO/I": "HEO"
}
df["Orbit_Group"] = df["OpOrbit"].map(orbit_map).fillna("Other")

app = Dash(__name__)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Fix dropdown option text colors */
            .Select-menu-outer {
                background-color: #1f2c56 !important;
            }
            .VirtualizedSelectOption {
                background-color: #1f2c56 !important;
                color: white !important;
            }
            .VirtualizedSelectFocusedOption {
                background-color: #3a4d80 !important;
                color: white !important;
            }
            /* Style for dropdown value text */
            .Select-value-label {
                color: white !important;
            }
            .Select-placeholder {
                color: #87CEEB !important;
            }
            .Select--single > .Select-control .Select-value, .Select-placeholder {
                color: white !important;
            }
            input[type="radio"] {
                accent-color: #87CEEB;  /* Light sky blue for visibility */
                z-index: 1 !important;
            }

            input[type="radio"]:checked::before {
                background-color: #87CEEB !important;
            }

            label[for^="status-radio"] {
                z-index: 2 !important;
            }

        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Stars
num_stars = 100
np.random.seed(42)
tops = np.random.uniform(0, 100, num_stars)
lefts = np.random.uniform(0, 100, num_stars)

stars = html.Div(
    [
        html.Span("✦", style={
            "position": "absolute",
            "top": f"{t:.2f}%",
            "left": f"{l:.2f}%",
            "color": "white",
            "fontSize": "0.2rem",
            "zIndex": 0
        }) for t, l in zip(tops, lefts)
    ],
    style={
        "position": "absolute",
        "top": 0,
        "left": 0,
        "width": "100%",
        "height": "100%",
        "zIndex": 0
    }
)

# Background Images
"""
To load the images on the dashboard, keep the folder "assets" which contains all the background images,
along with this python file in the same folder.

"""
background_images = html.Div([
    html.Img(src="/assets/real_moon.png",
             style={"position": "absolute", "bottom": "0%", "left": "12px", "width": "10%"}),
    html.Img(src="/assets/real_planet.png",
             style={"position": "absolute", "bottom": "24%", "right": "0%", "width": "10%"}),
    html.Img(src="/assets/real_saturn.png",
             style={"position": "absolute", "top": "-2.3%", "right": "4%", "width": "17%"}),
    html.Img(src="/assets/real_neptune.png", style={"position": "absolute", "top": "1.5%", "left": "3%", "width": "12%"}),
    html.Img(src="/assets/real_venus.png",
             style={"position": "absolute", "bottom": "39%", "left": "20%", "width": "15%"}),
    html.Img(src="/assets/real_earth.png",
             style={"position": "absolute", "bottom": "-18%", "left": "27%", "width": "10%"}),
    html.Img(src="/assets/real_jupiter.png",
             style={"position": "absolute", "bottom": "-18%", "right": "38%", "width": "10%"}),
    html.Img(src="/assets/sat.png", style={"position": "absolute", "bottom": "-17%", "right": "4%", "width": "20%"})
], style={
    "position": "absolute",
    "top": 0,
    "left": 0,
    "width": "100%",
    "height": "100%",
    "zIndex": 0.2,
    "opacity": 0.5,
    "pointerEvents": "none"
})

# Main layout
app.layout = html.Div([
    stars,
    background_images,
    html.H1("Satellite Lifespan and Decommissioning", style={"color": "white", "textAlign": "center"}),

    # Main content area - filters and graphs
    html.Div([
        # Filters panel
        html.Div([
            html.Div([
                html.Label("Launch Decade Range", style={"color": "white"}),
                dcc.RangeSlider(
                    id='decade-slider',
                    min=1950, max=2020, step=10, value=[1980, 2020],
                    marks={d: {"label": str(d), "style": {"color": "white"}} for d in range(1950, 2031, 10)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={"marginBottom": "20px"}),

            html.Div([
                html.Label("Mass Range (kg)", style={"color": "white"}),
                dcc.RangeSlider(
                    id='mass-slider',
                    min=0, max=10000, step=100, value=[0, 5000],
                    marks={i: {"label": str(i), "style": {"color": "white"}} for i in range(0, 10001, 2000)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={"marginBottom": "20px"}),

            html.Div([
                html.Label("Orbit Type", style={"color": "white"}),
                dcc.Dropdown(
                    id='orbit-dropdown',
                    options=[
                        {'label': 'All', 'value': 'All'},
                        {'label': 'Low Earth Orbit (LEO)', 'value': 'LEO'},
                        {'label': 'Geostationary Orbit (GEO)', 'value': 'GEO'},
                        {'label': 'Medium Earth Orbit (MEO)', 'value': 'MEO'},
                        {'label': 'High Earth Orbit (HEO)', 'value': 'HEO'},
                        {'label': 'Other', 'value': 'Other'}
                    ],
                    value='All',
                    style={"backgroundColor": "#1f2c56", "color": "white"}
                )
            ], style={"marginBottom": "20px"}),

            html.Div([
                html.Label("Status", style={"color": "white"}),
                dcc.RadioItems(
                    id='status-radio',
                    options=[
                        {'label': 'All', 'value': 'All'},
                        {'label': 'Active', 'value': 'Active'},
                        {'label': 'Decommissioned', 'value': 'Decommissioned'}
                    ],
                    value='All',
                    labelStyle={'display': 'block', 'color': 'white'}
                )
            ], style={"marginBottom": "20px"}),
           
            html.Div(id='plot-description', style={
                "color": "white",
                "marginTop": "30px",
                "fontSize": "16px",
                "lineHeight": "1.6",
                "whiteSpace": "pre-wrap"
            })


        ], style={
            "flex": "1 1 300px",  
            "minWidth": "280px",

            "vertical-align": "top",
            "padding": "20px",
            "backgroundColor": "rgba(25, 25, 50, 0.7)",
            "borderRadius": "10px",
            "position": "relative",
            "marginRight": "20px"
        }),

        # Graphs panel
        html.Div([
            html.Div([
                dcc.Tabs(
                    id='tabs',
                    value='tab-1',
                    children=[
                        dcc.Tab(label='Lifespan Trends Over Time', value='tab-1', children=[
                            html.Div(dcc.Graph(id='lifespan-graph'))
                        ], style={"backgroundColor": "#1f2c56", "color": "white"},
                                selected_style={"backgroundColor": "#3a4d80", "color": "white"}),

                        dcc.Tab(label='Are Satellites Being Retired Responsibly?', value='tab-2', children=[
                            html.Div(dcc.Graph(id='lifespan-hist'))
                        ], style={"backgroundColor": "#1f2c56", "color": "white"},
                                selected_style={"backgroundColor": "#3a4d80", "color": "white"}),

                        dcc.Tab(label='Where Are Decommissioned Satellites Located?', value='tab-3', children=[
                            html.Div(dcc.Graph(id='orbit-pie'))
                        ], style={"backgroundColor": "#1f2c56", "color": "white"},
                                selected_style={"backgroundColor": "#3a4d80", "color": "white"})
                    ],
                    style={"color": "white"}
                )
            ], style={"position": "relative", "zIndex": 1})
        ], style={
            "flex": "2 1 500px",  
            "minWidth": "400px",  

            "vertical-align": "top",
            "backgroundColor": "rgba(25, 25, 50, 0.7)",
            "borderRadius": "10px"
        })
    ], style={"display": "flex", "flexWrap": "wrap","alignItems": "flex-start" }),

    # Stats cards
    html.Div([
        html.Div([
            html.H4("Total Satellites", style={"color": "white", "textAlign": "center"}),
            html.Div(id='total-satellites', style={"color": "white", "textAlign": "center", "fontSize": "24px"})
        ], style={"width": "24%", "display": "inline-block", "backgroundColor": "rgba(25, 25, 50, 0.7)",
                  "borderRadius": "10px", "padding": "10px", "marginRight": "1%"}),
        html.Div([
            html.H4("Active Satellites", style={"color": "white", "textAlign": "center"}),
            html.Div(id='active-satellites', style={"color": "white", "textAlign": "center", "fontSize": "24px"})
        ], style={"width": "24%", "display": "inline-block", "backgroundColor": "rgba(25, 25, 50, 0.7)",
                  "borderRadius": "10px", "padding": "10px", "marginRight": "1%"}),
        html.Div([
            html.H4("Average Lifespan (years)", style={"color": "white", "textAlign": "center"}),
            html.Div(id='avg-lifespan', style={"color": "white", "textAlign": "center", "fontSize": "24px"})
        ], style={"width": "24%", "display": "inline-block", "backgroundColor": "rgba(25, 25, 50, 0.7)",
                  "borderRadius": "10px", "padding": "10px", "marginRight": "1%"}),
        html.Div([
            html.H4("Average Mass (kg)", style={"color": "white", "textAlign": "center"}),
            html.Div(id='avg-mass', style={"color": "white", "textAlign": "center", "fontSize": "24px"})
        ], style={"width": "24%", "display": "inline-block", "backgroundColor": "rgba(25, 25, 50, 0.7)",
                  "borderRadius": "10px", "padding": "10px"})
    ], style={"marginTop": "20px", "padding": "10px"})
], style={"backgroundColor": "#111122", "fontFamily": "Arial", "minHeight": "100vh", "padding": "20px"})


@app.callback(
    [
        Output('lifespan-graph', 'figure'),
        Output('lifespan-hist', 'figure'),
        Output('orbit-pie', 'figure'),
        Output('total-satellites', 'children'),
        Output('active-satellites', 'children'),
        Output('avg-lifespan', 'children'),
        Output('avg-mass', 'children'),
        Output('plot-description', 'children')
    ],
    [
        Input('decade-slider', 'value'),
        Input('mass-slider', 'value'),
        Input('orbit-dropdown', 'value'),
        Input('status-radio', 'value'),
        Input('tabs', 'value')
    ]
)
def update_graphs(decade_range, mass_range, orbit_type, status, tab):
    # Initial filter
    filtered_df = df[
        (df['Launch_Decade'] >= decade_range[0]) &
        (df['Launch_Decade'] <= decade_range[1]) &
        (df['Mass'] >= mass_range[0]) &
        (df['Mass'] <= mass_range[1])
        ]

    # Status filter 
    if status != 'All':
        is_active = True if status == 'Active' else False
        filtered_df = filtered_df[filtered_df['IsActive'] == is_active]

    # Orbit filter
    if orbit_type != 'All':
        filtered_df = filtered_df[filtered_df['Orbit_Group'] == orbit_type]

    # Create empty figures in case of no data
    empty_fig = go.Figure()
    empty_fig.update_layout(
        title="Oops! Nothing to display. The data for this criteria is unavailable.",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=500
    )

    # Set default description based on tab
    if tab == 'tab-1':
        desc = "Satellite lifespans have changed over time. Early satellites lasted only a few years, but by the 1990s, better technology meant they stayed active much longer. Recently, the rise of small, low-cost satellites like CubeSats has led to shorter lifespans again—raising concerns about growing space clutter and long-term sustainability."
    elif tab == 'tab-2':
        desc = "Most satellites are never removed after they stop working. While launches have increased each decade, so has the number of inactive satellites left behind. Many older satellites—especially from the 1990s and 2000s—weren't designed to safely deorbit, adding to the growing clutter in space."
    elif tab == 'tab-3':
        desc = "Most retired satellites stay in low Earth orbit (LEO). As more small satellites and mega-constellations are launched, LEO is becoming crowded—not just with working satellites, but also with space junk. If this isn't managed, it could threaten future missions."
    else:
        desc = ""

    # Check if filtered_df is empty
    if filtered_df.empty:
        return empty_fig, empty_fig, empty_fig, "0", "0", "0", "0", desc

    # Figure 1: KDE Lifespan Distribution
    lifespan_fig = go.Figure()
    try:
        overlap = 0.5
        max_lifespan = filtered_df['Lifespan_Years'].max()
        if max_lifespan <= 0:
            max_lifespan = 1  # Ensure we have a valid range
        x_grid = np.linspace(0, max_lifespan, 500)
        decade_order = sorted(filtered_df['Launch_Decade'].dropna().unique())
        
        # Define a color palette
        colors = [
            "rgba(0, 191, 255, 0.7)",   
            "rgba(65, 105, 225, 0.7)",  
            "rgba(70, 130, 180, 0.7)",  
            "rgba(100, 149, 237, 0.7)", 
            "rgba(30, 144, 255, 0.7)",  
            "rgba(255, 255, 255, 0.8)",     
            "rgba(25, 25, 112, 0.7)",   
            "rgba(0, 0, 255, 0.7)",     
            "rgba(135, 206, 250, 0.7)", 
            "rgba(0, 0, 205, 0.7)"        
        ]
        for i, decade in enumerate(decade_order):
            group = filtered_df[filtered_df["Launch_Decade"] == decade]
            if len(group) < 5:  # Need more points for stable KDE
                continue
            try:
                kde = gaussian_kde(group["Lifespan_Years"].dropna(), bw_method=0.5)
                y = kde(x_grid)
                if y.max() > 0:
                    y = y / y.max()  # Normalize, prevent division by zero
                else:
                    continue  # Skip if all values are zero
                offset = i * overlap
                
                # Use color from our palette
                color_index = i % len(colors)
                
                lifespan_fig.add_trace(go.Scatter(
                    x=x_grid,
                    y=y + offset,
                    mode="lines",
                    fill="tonexty",
                    name=f"{decade}s",
                    hoverinfo='x+y+name',
                    line=dict(width=2),
                    fillcolor=colors[color_index]
                ))
            except Exception:
                continue  # Skip this decade if KDE fails
    except Exception:
        lifespan_fig = empty_fig

    # Update layout only if we added traces
    if len(lifespan_fig.data) > 0:
        lifespan_fig.update_layout(
            title="How Satellite Lifespans Have Changed Over the Decades",
            xaxis_title="Lifespan (Years)",
            yaxis=dict(showticklabels=False, title="Launch Decade (stacked)", zeroline=False),
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=500,
            hovermode="closest",
            margin=dict(t=40, b=40, l=40, r=40)
        )
    else:
        lifespan_fig = empty_fig

    # Figure 2: Bar chart of Active vs Inactive satellites
    bar_fig = go.Figure()
    try:
        # Ensure we have data before grouping
        if not filtered_df.empty:
            # Create status_counts DataFrame - handle potential groupby errors
            status_counts = pd.DataFrame(index=filtered_df['Launch_Decade'].unique())
            
            # Get counts for each status
            active_counts = filtered_df[filtered_df['IsActive'] == True].groupby('Launch_Decade').size()
            inactive_counts = filtered_df[filtered_df['IsActive'] == False].groupby('Launch_Decade').size()
            
            # Assign to status_counts, handling missing values
            status_counts[True] = active_counts.reindex(status_counts.index, fill_value=0)
            status_counts[False] = inactive_counts.reindex(status_counts.index, fill_value=0)
            
            # Sort index for consistent display
            status_counts = status_counts.sort_index()

            # Decommissioned bar
            bar_fig.add_trace(go.Bar(
                x=status_counts.index,
                y=status_counts[False],
                name="Decommissioned",
                marker_color="rgba(0, 191, 255, 0.7)",
                customdata=[["Decommissioned"]] * len(status_counts),
                hovertemplate="Decade: %{x}<br>Count: %{y}<br>Status: %{customdata[0]}<extra></extra>"
            ))

            # Active bar
            bar_fig.add_trace(go.Bar(
                x=status_counts.index,
                y=status_counts[True],
                name="Active",
                marker_color="rgba(255, 255, 255, 0.8)",
                customdata=[["Active"]] * len(status_counts),
                hovertemplate="Decade: %{x}<br>Count: %{y}<br>Status: %{customdata[0]}<extra></extra>"
            ))

            bar_fig.update_layout(
                barmode='stack',
                title="Active vs Decommissioned Satellites by Launch Decade",
                xaxis_title="Launch Decade",
                yaxis_title="Number of Satellites",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=500,
                legend=dict(
                    title='Status',
                    font=dict(size=14, color='white'),
                    bgcolor='rgba(25,25,50,0.7)'
                ),
                margin=dict(t=40, b=40, l=40, r=40)
            )
        else:
            bar_fig = empty_fig
    except Exception as e:
        print(f"Error in bar chart: {e}")
        bar_fig = empty_fig

    # Figure 3: Orbit distribution
    bar_orbit_fig = go.Figure()
    try:
        inactive_df = filtered_df[~filtered_df["IsActive"]].copy()

        # Check if we have inactive satellites
        if not inactive_df.empty:
            # Safely create orbit_grouped DataFrame
            orbit_counts = inactive_df.groupby(["Launch_Decade", "Orbit_Group"]).size().reset_index(name='count')
            
            if not orbit_counts.empty:
                # Get top orbit groups
                orbit_sums = orbit_counts.groupby("Orbit_Group")['count'].sum().sort_values(ascending=False)
                top_orbit_groups = orbit_sums.head(4).index.tolist()
                
                # Define colors
                colors = [
                    "rgba(0, 191, 255, 0.7)",   # deep sky blue
                    "rgba(255, 255, 255, 0.8)",  # white-ish
                    "#ffd700",                  # yellowish
                    "#ff6347"                   # redish
                ]

                # Filter for just the top orbits
                for i, orbit in enumerate(top_orbit_groups):
                    orbit_data = orbit_counts[orbit_counts["Orbit_Group"] == orbit]
                    
                    if i < len(colors) and not orbit_data.empty:
                        bar_orbit_fig.add_trace(go.Bar(
                            x=orbit_data["Launch_Decade"],
                            y=orbit_data["count"],
                            name=orbit,
                            marker_color=colors[i],
                            hovertemplate="Decade: %{x}<br>Count: %{y}<br>Orbit: " + orbit + "<extra></extra>"
                        ))

                bar_orbit_fig.update_layout(
                    barmode='group',
                    title="Top Orbit Types Where Decommissioned Satellites Accumulate",
                    xaxis_title="Launch Decade",
                    yaxis_title="Number of Inactive Satellites",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    height=500,
                    legend=dict(
                        title='Orbit Group',
                        font=dict(size=14, color='white'),
                        bgcolor='rgba(25,25,50,0.7)'
                    ),
                    margin=dict(t=40, b=40, l=40, r=40)
                )
            else:
                bar_orbit_fig = empty_fig
        else:
            bar_orbit_fig = empty_fig
    except Exception as e:
        print(f"Error in orbit chart: {e}")
        bar_orbit_fig = empty_fig

    # Calculate statistics safely
    try:
        total_satellites = str(len(filtered_df))
        active_satellites = str(filtered_df['IsActive'].sum())

        if len(filtered_df) > 0:
            # Handle potential NaN values
            lifespan_values = filtered_df['Lifespan_Years'].dropna()
            if len(lifespan_values) > 0:
                avg_lifespan = str(round(lifespan_values.mean(), 1))
            else:
                avg_lifespan = "0"

            mass_values = filtered_df['Mass'].dropna()
            if len(mass_values) > 0:
                avg_mass = str(round(mass_values.mean(), 1))
            else:
                avg_mass = "0"
        else:
            avg_lifespan = "0"
            avg_mass = "0"
    except Exception as e:
        print(f"Error calculating stats: {e}")
        total_satellites = "0"
        active_satellites = "0"
        avg_lifespan = "0"
        avg_mass = "0"

    return lifespan_fig, bar_fig, bar_orbit_fig, total_satellites, active_satellites, avg_lifespan, avg_mass, desc

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
