import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from streamlit_folium import st_folium
from pathlib import Path

from bloom.config import settings
from bloom.infra.database.database_manager import Database
from bloom.infra.repositories.repository_vessel import RepositoryVessel

st.set_page_config(page_title="Vessel Exploration", page_icon="⚓", layout="wide")


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


local_css(Path(__file__).parent.parent.joinpath("./styles.css"))

db = Database(settings.db_url)
rep = RepositoryVessel(db.session)


# @st.cache_data  # 👈 Add the caching decorator
def load_trajectory(mmsi, mpa):
    vessel = rep.get_vessel_trajectory(mmsi)
    if mpa:
        vessel.get_closest_marine_protected_areas()
    return vessel


# @st.cache_data  # 👈 Add the caching decorator
def load_trawlers():
    trawlers = pd.read_csv(Path(settings.data_folder).joinpath("./chalutiers_pelagiques.csv"), sep=";")
    return trawlers


# -------------------------------------------------------------------------------
# Vessel selection

trawlers = load_trawlers()
options_names = [None, *list(trawlers["ship_name"].unique())]
options = [
    None,
    246014000,
    224068000,
    277510000,
    205775000,
    224048290,
    228110000,
    263576000,
    224148000,
    238561110,
    237034000,
]
other_mmsis = [
    int(x)
    for x in list(trawlers["mmsi"].unique())
    if not pd.isnull(x) and int(x) not in options[1:]
]
options = options + other_mmsis

if "vessel_mmsi" not in st.session_state:
    st.session_state.vessel_mmsi = None


def select_vessel(mmsi):
    st.session_state.vessel_mmsi = mmsi


with st.sidebar.form("Vessel selection"):
    mmsi = st.selectbox("Select from vessel MMSI", options)
    load_mpa = st.checkbox("Load MPA")
    submitted = st.form_submit_button("Load", on_click=select_vessel, args=(mmsi,))

# -------------------------------------------------------------------------------
# Vessel exploration main page

if st.session_state.vessel_mmsi is None:
    st.write("Select a vessel from the dropdown list")

else:
    mmsi = str(st.session_state.vessel_mmsi)
    v = load_trajectory(mmsi, load_mpa)

    # if "mpas" not in st.session_state:
    #     if hasattr(v,"_mpas"):

    st.sidebar.write(f"### Vessel *{v.metadata['ship_name']}*")
    st.sidebar.write(v.metadata)

    col1, col2, col3 = st.columns(3)

    st.session_state.range = (0, len(v.positions))

    def change_range(voyage_id):
        vf = v.positions.query(f"voyage_id=={voyage_id}")
        min_value = int(vf.index.min())
        max_value = int(vf.index.max())
        st.session_state.range = (min_value, max_value)

    with col1:
        if "voyage_id" not in st.session_state:
            st.session_state.voyage_id = 0
            change_range(0)

        voyage_id = st.slider("Voyage id", min_value=0, max_value=v.n_voyages)
        if voyage_id != st.session_state.voyage_id:
            change_range(voyage_id)

        vi = v.query(voyage_id=voyage_id)
        vi.positions = v.positions.copy()

    with col2:
        min_value, max_value = st.slider(
            "Chunk id",
            min_value=0,
            max_value=len(v.positions),
            value=st.session_state.range,
            step=5,
        )
        vi.positions = vi.positions.loc[min_value:max_value]

    with col3:
        show_markers_fishing = st.checkbox("See fishing marker")
        show_mpas = st.checkbox("See marine protected areas")

    col1, col2, col3, col4 = st.columns(4)
    col1.write(f"From: {str(vi.positions['timestamp'].min())[:19]}")
    col1.write(f"To: {str(vi.positions['timestamp'].max())[:19]}")
    col2.metric("Records", len(vi.positions))
    col3.metric(
        "Duration",
        str(vi.positions["timestamp"].max() - vi.positions["timestamp"].min()).split(
            ".",
        )[0][:-3],
    )
    col4.metric("Average speed", round(vi.positions["speed"].mean(), 2))

    if show_mpas:
        vi.get_closest_marine_protected_areas()

    folium_map = vi.visualize_trajectory(
        marker_by_fishing=show_markers_fishing,
        show_mpas=show_mpas,
        show_iucn=True,
    )

    # call to render Folium map in Streamlit
    st_folium(folium_map, width=2000, returned_objects=[])

    # if reload_mpas:
