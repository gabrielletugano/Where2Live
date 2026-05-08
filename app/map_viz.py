"""
map_viz.py
Builds the Folium choropleth map from a scored GeoDataFrame.
"""

import folium
import geopandas as gpd
import json


def build_map(scored_gdf: gpd.GeoDataFrame) -> folium.Map:
    """
    Render a choropleth map of Boston neighborhoods colored by livability score.
    Returns a Folium Map object ready to embed in Streamlit via streamlit-folium.
    """
    m = folium.Map(
        location=[42.3201, -71.0889],
        zoom_start=12,
        tiles="CartoDB positron",
    )

    geojson_data = json.loads(scored_gdf.to_json())

    folium.Choropleth(
        geo_data=geojson_data,
        data=scored_gdf,
        columns=["Name", "livability_score"],
        key_on="feature.properties.Name",
        fill_color="RdYlGn",
        fill_opacity=0.75,
        line_opacity=0.4,
        legend_name="Livability Score (0–100)",
        nan_fill_color="lightgrey",
    ).add_to(m)

    # Invisible overlay for hover tooltips
    folium.GeoJson(
        geojson_data,
        tooltip=folium.GeoJsonTooltip(
            fields=[
                "Name",
                "livability_score",
                "transit_score",
                "safety_score",
                "green_score",
                "restaurant_score",
            ],
            aliases=[
                "Neighborhood",
                "Overall Score",
                "Transit",
                "Safety",
                "Green Space",
                "Restaurants",
            ],
            localize=True,
        ),
        style_function=lambda x: {"fillOpacity": 0, "weight": 0},
    ).add_to(m)

    return m