import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import plotly.express as px

@st.cache_data
def create_map():
    df = pd.read_csv("stores.csv")
    df = df.dropna()

    name, name_e, geometry, lon, lat = [], [], [], [], []
    for _, r in df.iterrows():
        name.append(r["name"])
        name_e.append(r["name-e"])
        lon.append(r["lon"])
        lat.append(r["lat"])
        geometry.append(Point(r["lon"], r["lat"]))

    d = {"name": name, "name-e": name_e, "geometry": geometry, "lat":lat, "lon":lon}
    storedf = gpd.GeoDataFrame(d)

    fig = px.scatter_mapbox(storedf, 
                        lat="lat", 
                        lon="lon", 
                        hover_name="name",
                        mapbox_style="stamen-terrain", 
                        zoom=9, height=900)
    return fig

st.set_page_config("Kakuyasu map", layout="wide")

fig = create_map()
st.plotly_chart(fig, use_container_width=True)