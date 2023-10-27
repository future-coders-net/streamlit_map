import streamlit as st
import pandas as pd
import pykakasi
from streamlit_folium import st_folium
import folium
import osmnx as ox

kks = pykakasi.kakasi()

def kana(s):
    r = []
    for kana in kks.convert(s):
        r.append(kana["hepburn"])
    return "-".join(r)

st.set_page_config("Kakuyasu map", layout="wide")
st.title("KAKUYASU MAP")

@st.cache_data
def get_G():
    query = "Tokyo,Japan"
    G = ox.graph_from_place(query, network_type="drive") 
    return G

@st.cache_data
def create_df():
    df = pd.read_csv("stores.csv")
    df = df.dropna()
    return df

df = create_df()
categories = df.area.unique()

with st.sidebar:
    st.subheader("Category")
    for ct in categories:
        st.checkbox(ct, key=ct)
        st.caption(kana(ct))

selected_areas = [k for k, v in st.session_state.items() if k in categories and v]
df_selected = df[
    df.area.isin(selected_areas)
]

map = folium.Map(location=[35.646351,139.73134149999998], zoom_start=10)

for i, row in df_selected.iterrows():
    color = "red" if row["area"] == "配達専用出荷ステーション" else "blue"

    folium.Marker(
        [row.lat, row.lon],
        popup=f"{row['name']}\n{row['name-e']}", 
        icon=folium.Icon(color=color)
    ).add_to(map)

st.subheader("LOCATIONS")
st.components.v1.html(folium.Figure().add_child(map).render(), height=700)


st.subheader("Routes")
st.write("route from Shirogane-ten (in 20 min without any traffic jam)")
st.image("image.png")
