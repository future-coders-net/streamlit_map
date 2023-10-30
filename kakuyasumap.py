import streamlit as st
import pandas as pd
import pykakasi
from streamlit_folium import st_folium
import folium
import osmnx as ox
import networkx as nx

kks = pykakasi.kakasi()

def kana(s):
    r = []
    for kana in kks.convert(s):
        r.append(kana["hepburn"])
    return "-".join(r)

st.set_page_config("Kakuyasu map", layout="wide")
st.title("KAKUYASU MAP")

@st.cache_data
def get_Route_Map_Of_Tokyo():
    wards = ['Adachi, Tokyo, Japan', 'Arakawa, Tokyo, Japan', 'Bunkyo, Tokyo, Japan', 
         'Chiyoda, Tokyo, Japan', 'Chuo, Tokyo, Japan', 'Edogawa, Tokyo, Japan', 
         'Itabashi, Tokyo, Japan', 'Katsushika, Tokyo, Japan', 'Kita, Tokyo, Japan', 
         'Koto, Tokyo, Japan', 'Meguro, Tokyo, Japan', 'Minato, Tokyo, Japan', 
         'Nakano, Tokyo, Japan', 'Nerima, Tokyo, Japan', 'Ota, Tokyo, Japan', 
         'Setagaya, Tokyo, Japan', 'Shibuya, Tokyo, Japan', 'Shinagawa, Tokyo, Japan', 
         'Shinjuku, Tokyo, Japan', 'Suginami, Tokyo, Japan', 'Sumida, Tokyo, Japan', 
         'Taito, Tokyo, Japan', 'Toshima, Tokyo, Japan']

    st.spinner(text="In progress...Wait for a while... it takes 2-3 min for the first time.")
    G = ox.graph_from_place(wards, network_type="drive") 
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
    
    st.subheader("Routes")
    ds_df = df[df["area-e"] == "haitatsu-senyou-shukka-suteeshon"]
    st.selectbox("Distribution Center", ds_df["name"], key="ds")

    store_df = df[df["area-e"] == "toukyou-23-kunai-no-tenpo"]
    st.selectbox("Store ", store_df["name"], key="store")

    st.button("route", key="route")
    

selected_areas = [k for k, v in st.session_state.items() if k in categories and v]
df_selected = df[
    df.area.isin(selected_areas)
]

map = folium.Map(location=[35.646351,139.73134149999998], zoom_start=12)

for i, row in df_selected.iterrows():
    color = "red" if row["area"] == "配達専用出荷ステーション" else "blue"

    folium.Marker(
        [row.lat, row.lon],
        popup=f"{row['name']}\n{row['name-e']}", 
        icon=folium.Icon(color=color)
    ).add_to(map)

st.subheader("LOCATIONS")
st.components.v1.html(folium.Figure().add_child(map).render(), height=700)

if st.session_state.route:
    ds = st.session_state.ds
    store = st.session_state.store
    from_lat_lon = df[df["name"] == ds][["lat", "lon"]]
    to_lat_lon = df[df["name"] == store][["lat", "lon"]]
    st.write(f"{ds}:{from_lat_lon} to {store}:{to_lat_lon} {type(to_lat_lon)}")

    G = get_Route_Map_Of_Tokyo()
    from_node = ox.distance.nearest_nodes(G, from_lat_lon["lon"], from_lat_lon["lat"])
    to_node = ox.distance.nearest_nodes(G, to_lat_lon["lon"], to_lat_lon["lat"])

    try:
        route = nx.shortest_path(G, from_node[0], to_node[0], weight='travel_time')
        nodes = [G.nodes[r] for r in route]
        # st.write(nodes)
        # f = ox.plot_graph_routes(G, [route, route],
        #     route_colors='blue', route_linewidth=0.5, node_size=0.1)
        #     # f = <class 'matplotlib.figure.Figure'> <class 'matplotlib.axes._axes.Axes'>
        routes = [[n['y'], n['x']] for n in nodes]
        folium.PolyLine(routes, color="red", weight=2.5, opacity=1).add_to(map)
        st.components.v1.html(folium.Figure().add_child(map).render(), height=700)
    except Exception as e:
        st.write(f"location not found.{e}")


st.subheader("Routes")
st.write("route from Shirogane-ten (in 20 min without any traffic jam)")
st.image("image.png")
