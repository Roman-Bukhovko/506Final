import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Load the refined data with labeled categories
df = pd.read_csv("refined_animal_classification.csv", low_memory=False)
df['open_dt'] = pd.to_datetime(df['open_dt'], errors='coerce')
df = df.dropna(subset=['latitude', 'longitude'])

# Manually map clusters to meaningful names
category_names = {
    0: "Dead Animal",
    1: "Stray Dog/Cat",
    2: "Animal Bite",
    3: "Aggressive Behavior",
    4: "Wildlife Sighting"
}

df["category_label"] = df["animal_category"].map(category_names)

# Start Dash app
app = dash.Dash(__name__)
app.title = "Refined Animal Case Dashboard"

app.layout = html.Div([
    html.H1("\U0001F43E Refined Animal Case Explorer", style={"textAlign": "center"}),

    html.Div([
        html.Label("Select Animal Category (Cluster):"),
        dcc.Dropdown(
            options=[{"label": name, "value": name} for name in sorted(df["category_label"].unique())],
            id="category-filter",
            multi=True,
            placeholder="Filter by refined category..."
        ),
    ], style={"width": "40%", "margin": "auto"}),

    dcc.Graph(id="case-time-series"),
    dcc.Graph(id="case-map")
])

# Callback to update plots based on filter
@app.callback(
    [Output("case-time-series", "figure"),
     Output("case-map", "figure")],
    [Input("category-filter", "value")]
)
def update_dashboard(selected_categories):
    filtered = df.copy()
    if selected_categories:
        filtered = filtered[filtered['category_label'].isin(selected_categories)]

    # Time series
    time_series = (
        filtered['open_dt'].dt.date
        .value_counts()
        .sort_index()
        .reset_index(name='count')
        .rename(columns={'index': 'open_dt'})
    )

    fig1 = px.line(time_series, x='open_dt', y='count',
                   title="Animal Cases Over Time")

    # Map visualization
    fig2 = px.scatter_mapbox(
        filtered,
        lat="latitude",
        lon="longitude",
        color="category_label",
        hover_name="case_title",
        zoom=11,
        mapbox_style="carto-positron",
        title="Map of Animal-Related Case Clusters"
    )

    return fig1, fig2

# Run the Dash server
if __name__ == "__main__":
    app.run(debug=True)
