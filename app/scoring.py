"""
scoring.py
Builds the composite livability index for each Boston neighborhood.
Each feature is min-max normalized to [0, 1], then weighted and summed.
"""

import pandas as pd
import geopandas as gpd
import numpy as np


def normalize(series: pd.Series) -> pd.Series:
    """Min-max normalize a Series to [0, 1]."""
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - mn) / (mx - mn)


def compute_transit_score(
    neighborhoods: gpd.GeoDataFrame, mbta_stops: gpd.GeoDataFrame
) -> pd.Series:
    """Count MBTA stops within each neighborhood polygon."""
    stops_in = gpd.sjoin(
        mbta_stops,
        neighborhoods[["Name", "geometry"]],
        how="left",
        predicate="within",
    )
    counts = stops_in.groupby("Name").size().reindex(neighborhoods["Name"], fill_value=0)
    return normalize(counts)


def compute_safety_score(
    neighborhoods: gpd.GeoDataFrame, crime: pd.DataFrame
) -> pd.Series:
    """
    Build a safety score as the inverse of crime rate.
    Note: Boston crime data uses police districts, not neighborhood names.
    A district -> neighborhood crosswalk is needed for full accuracy.
    Returns a uniform placeholder until the crosswalk is built.
    """
    # TODO: join crime DISTRICT column to neighborhood names via crosswalk
    scores = pd.Series(0.5, index=neighborhoods["Name"])
    return scores


def compute_green_score(
    neighborhoods: gpd.GeoDataFrame, parks: gpd.GeoDataFrame
) -> pd.Series:
    """Compute total park area (sq meters) per neighborhood via spatial join."""
    parks_proj = parks.to_crs("EPSG:3857")
    hoods_proj = neighborhoods[["Name", "geometry"]].to_crs("EPSG:3857")
    joined = gpd.sjoin(parks_proj, hoods_proj, how="left", predicate="within")
    joined["area"] = joined.geometry.area
    area_per_hood = (
        joined.groupby("Name")["area"]
        .sum()
        .reindex(neighborhoods["Name"], fill_value=0)
    )
    return normalize(area_per_hood)


def compute_restaurant_score(
    neighborhoods: gpd.GeoDataFrame, restaurants: pd.DataFrame
) -> pd.Series:
    """Normalize restaurant counts per neighborhood."""
    merged = neighborhoods[["Name"]].merge(
        restaurants, left_on="Name", right_on="neighborhood", how="left"
    )
    merged["restaurant_count"] = merged["restaurant_count"].fillna(0)
    return normalize(merged.set_index("Name")["restaurant_count"])


def build_index(
    neighborhoods: gpd.GeoDataFrame,
    transit_score: pd.Series,
    safety_score: pd.Series,
    green_score: pd.Series,
    restaurant_score: pd.Series,
    weights: dict,
) -> gpd.GeoDataFrame:
    """Combine individual scores into a single livability index (0–100)."""
    gdf = neighborhoods.copy().set_index("Name")
    gdf["transit_score"] = (transit_score * 100).round(1)
    gdf["safety_score"] = (safety_score * 100).round(1)
    gdf["green_score"] = (green_score * 100).round(1)
    gdf["restaurant_score"] = (restaurant_score * 100).round(1)
    gdf["livability_score"] = (
        (transit_score * weights["transit"])
        + (safety_score * weights["safety"])
        + (green_score * weights["green"])
        + (restaurant_score * weights["restaurants"])
    ) * 100
    gdf["livability_score"] = gdf["livability_score"].round(1)
    return gdf.reset_index()