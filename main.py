"""
main.py
Streamlit entry point for Where2Live.
Run with: streamlit run app/main.py
"""

import streamlit as st
from streamlit_folium import st_folium
from dotenv import load_dotenv
import pandas as pd
import os

from data_loader import load_neighborhoods, load_mbta_stops, load_parks, load_crime
from scoring import (
    compute_transit_score,
    compute_safety_score,
    compute_green_score,
    build_index,
)
from map_viz import build_map

load_dotenv()

st.set_page_config(page_title="Where2Live", page_icon="📍", layout="wide")

# --- Header ---
st.title("📍 Where2Live")
st.markdown(
    "A data-driven livability index for Boston neighborhoods. "
    "Adjust the sliders to weight what matters most to you."
)

# --- Sidebar: weight sliders ---
st.sidebar.header("Your Priorities")
w_transit = st.sidebar.slider("🚇 Transit Access", 0, 100, 30)
w_safety = st.sidebar.slider("🔒 Safety", 0, 100, 30)
w_green = st.sidebar.slider("🌳 Green Space", 0, 100, 20)
w_restaurants = st.sidebar.slider("🍽️ Restaurants", 0, 100, 20)

total = w_transit + w_safety + w_green + w_restaurants
if total == 0:
    st.sidebar.error("At least one weight must be greater than 0.")
    st.stop()

weights = {
    "transit": w_transit / total,
    "safety": w_safety / total,
    "green": w_green / total,
    "restaurants": w_restaurants / total,
}

st.sidebar.markdown("---")
st.sidebar.caption(
    f"Weights (normalized): Transit {weights['transit']:.0%} · "
    f"Safety {weights['safety']:.0%} · "
    f"Green {weights['green']:.0%} · "
    f"Restaurants {weights['restaurants']:.0%}"
)

# --- Load data ---
with st.spinner("Loading Boston data..."):
    neighborhoods = load_neighborhoods()
    mbta_stops = load_mbta_stops(api_key=os.getenv("MBTA_API_KEY"))
    parks = load_parks()
    crime = load_crime()

# --- Compute scores ---
transit_score = compute_transit_score(neighborhoods, mbta_stops)
safety_score = compute_safety_score(neighborhoods, crime)
green_score = compute_green_score(neighborhoods, parks)

# Placeholder restaurant score — swap in load_restaurants_yelp() when key is ready
restaurant_score = pd.Series(0.5, index=neighborhoods["Name"])

scored = build_index(
    neighborhoods, transit_score, safety_score, green_score, restaurant_score, weights
)

# --- Map ---
st.subheader("Boston Neighborhood Livability Map")
st.caption("Hover over a neighborhood to see its breakdown.")
m = build_map(scored)
st_folium(m, width=None, height=550, returned_objects=[])

# --- Leaderboard ---
st.subheader("Neighborhood Rankings")
display = (
    scored[
        [
            "Name",
            "livability_score",
            "transit_score",
            "safety_score",
            "green_score",
            "restaurant_score",
        ]
    ]
    .sort_values("livability_score", ascending=False)
    .reset_index(drop=True)
)
display.index += 1
display.columns = ["Neighborhood", "Overall", "Transit", "Safety", "Green Space", "Restaurants"]
st.dataframe(display.style.format(precision=1), use_container_width=True)