# Trip Planner (to be updated, when the app expands beyond simple trip planning)
# created by Adicus Ryan Garton
# for MLDE Fall 2026 project (Intro to Programming, Software Development Tools)

# Folium is a map module; Streamlit is the web GUI.
import streamlit as st
import folium
from streamlit_folium import st_folium

# Developer settings
DEBUG_MODE = False

import streamlit as st

st.title("Trip Planner")

st.write("""
Welcome to the Trip Planner application.

Use the sidebar to:
- Plan a route
- View detailed directions & maps
""")