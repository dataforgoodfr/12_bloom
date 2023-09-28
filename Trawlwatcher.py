import streamlit as st

st.set_page_config(
    page_title="Bloom Trawlwatcher Demo app",
    page_icon="🐟",
    layout="wide",
)


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


local_css("styles.css")

st.write("![](https://upload.wikimedia.org/wikipedia/fr/e/e8/Logo_BLOOM.jpg)")
st.write("## Welcome to Bloom Trawlwatcher Demo app! 🐟")

st.write(
    """
Trawlwatcher is a specialized application that processes and visualizes global AIS (Automatic Identification System) vessel data. It offers a platform to track real-time and historical vessel movements.

With a dedicated algorithm, Trawlwatcher can recognize distinct fishing behaviors based on patterns in vessel movement, providing invaluable information for effective fisheries management, maritime security, and marine conservation initiatives.

Trawlwatcher`s interactive map interface simplifies the process of visualizing vessel trajectories, converting intricate AIS data into easy-to-understand visual representations.

Significantly, the application includes an overlay of Marine Protected Areas (MPAs) on its maps, enabling users to keep track of these vital regions and increase awareness about potential disruptions and damaging activities.

""",
)
