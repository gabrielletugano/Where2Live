"""
data_loader.py
Handles all data fetching from Analyze Boston, MBTA, and Yelp APIs.
Results are cached to avoid repeated API calls during development.
"""

import requests
import pandas as pd
import geopandas as gpd
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

NEIGHBORHOODS_GEOJSON_URL = (
    "https://raw.githubusercontent.com/codeforboston/neighborhood-finder/master/data/"
    "neighborhoods.geojson"
)

CRIME_API_URL = "https://data.boston.gov/api/3/action/datastore_search"
CRIME_RESOURCE_ID = "12cb3883-56f5-47de-afa5-3b1cf61b257b"

PARKS_GEOJSON_URL = (
    "https://bostonopendata-boston.opendata.arcgis.com/datasets/"
    "2868d370c55d4d458d4ae2224ef8cddd_7.geojson"
)

MBTA_STOPS_URL = "https://api-v3.mbta.com/stops"


def load_neighborhoods() -> gpd.GeoDataFrame:
    cache = RAW_DIR / "Boston_Neighborhoods.geojson"
    if cache.exists():
        return gpd.read_file(cache)
    raise FileNotFoundError("Download neighborhoods.geojson "
                            "from data.boston.gov and place it in data/raw/")


def load_crime(year: int = 2023) -> pd.DataFrame:
    """Fetch crime incidents from Analyze Boston for a given year."""
    cache = RAW_DIR / f"crime_{year}.csv"
    if cache.exists():
        return pd.read_csv(cache)
    params = {
        "resource_id": CRIME_RESOURCE_ID,
        "limit": 50000,
        "filters": f'{{"YEAR":"{year}"}}',
    }
    r = requests.get(CRIME_API_URL, params=params)
    r.raise_for_status()
    records = r.json()["result"]["records"]
    df = pd.DataFrame(records)
    df.to_csv(cache, index=False)
    return df


def load_parks() -> gpd.GeoDataFrame:
    """Load Boston parks / open space as a GeoDataFrame."""
    cache = RAW_DIR / "parks.geojson"
    if cache.exists():
        return gpd.read_file(cache)
    gdf = gpd.read_file(PARKS_GEOJSON_URL)
    gdf.to_file(cache, driver="GeoJSON")
    return gdf


def load_mbta_stops(api_key: str | None = None) -> gpd.GeoDataFrame:
    """Fetch MBTA subway + light rail stops."""
    cache = RAW_DIR / "mbta_stops.geojson"
    if cache.exists():
        return gpd.read_file(cache)
    headers = {"x-api-key": api_key} if api_key else {}
    params = {"filter[route_type]": "0,1"}  # light rail + heavy rail
    r = requests.get(MBTA_STOPS_URL, headers=headers, params=params)
    r.raise_for_status()
    stops = r.json()["data"]
    records = [
        {
            "stop_id": s["id"],
            "name": s["attributes"]["name"],
            "lat": s["attributes"]["latitude"],
            "lon": s["attributes"]["longitude"],
        }
        for s in stops
    ]
    df = pd.DataFrame(records).dropna(subset=["lat", "lon"])
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326"
    )
    gdf.to_file(cache, driver="GeoJSON")
    return gdf


def load_restaurants_yelp(api_key: str, neighborhoods: list[str]) -> pd.DataFrame:
    """
    Fetch restaurant counts per neighborhood from Yelp Fusion API.
    Iterates over neighborhood names and queries Boston restaurants.
    """
    cache = RAW_DIR / "restaurants.csv"
    if cache.exists():
        return pd.read_csv(cache)
    headers = {"Authorization": f"Bearer {api_key}"}
    results = []
    for hood in neighborhoods:
        params = {
            "location": f"{hood}, Boston, MA",
            "categories": "restaurants",
            "limit": 1,
        }
        r = requests.get(
            "https://api.yelp.com/v3/businesses/search",
            headers=headers,
            params=params,
        )
        if r.status_code == 200:
            total = r.json().get("total", 0)
            results.append({"neighborhood": hood, "restaurant_count": total})
    df = pd.DataFrame(results)
    df.to_csv(cache, index=False)
    return df