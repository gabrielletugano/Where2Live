# 📍 Where2Live

A data-driven neighborhood livability index for Boston, built with Python, GeoPandas, Folium, and Streamlit.

## What it does

Where2Live scores every Boston neighborhood across four dimensions:
- 🚇 **Transit access** — MBTA stop density
- 🔒 **Safety** — inverse crime rate (Analyze Boston)
- 🌳 **Green space** — park area per neighborhood
- 🍽️ **Restaurant density** — Yelp Fusion API

Users can adjust the weights of each factor via sliders to define what "livability" means to them.

## Tech stack

| Tool | Purpose |
|---|---|
| Streamlit | Frontend app |
| GeoPandas | Spatial joins + neighborhood mapping |
| Folium | Interactive choropleth map |
| Analyze Boston API | Crime + parks + boundaries data |
| MBTA API | Transit stop locations |
| Yelp Fusion API | Restaurant counts |

## Setup

```bash
git clone https://github.com/yourusername/where2live
cd where2live
pip install -r requirements.txt
cp .env.example .env  # add your API keys
streamlit run app/main.py
```

## Data sources

- [Analyze Boston](https://data.boston.gov/)
- [MBTA Developer Portal](https://api-v3.mbta.com/)
- [Yelp Fusion API](https://www.yelp.com/developers)

## Roadmap

- [ ] Add year-over-year crime trend
- [ ] Address search + neighborhood highlight
- [ ] "Best neighborhood for..." recommender presets
- [ ] Regression model predicting livability from raw features
