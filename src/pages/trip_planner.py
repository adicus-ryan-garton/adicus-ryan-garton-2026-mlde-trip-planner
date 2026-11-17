import folium
from streamlit_folium import st_folium

import streamlit as st
from geopy.geocoders import Nominatim

# Page title
st.title("Trip Planner")

# Ask the user for a starting point and destination
origin = st.text_input("Starting location")
destination = st.text_input("Destination")


def get_coordinates(place):
    """
    Convert a place name into latitude/longitude coordinates.
    """

    # timeout=10 gives the server more time to respond
    geolocator = Nominatim(
        user_agent="trip_planner",
        timeout=10
    )

    location = geolocator.geocode(place)

    if location:
        return (location.latitude, location.longitude)

    return None

# Create the session variable the first time the page loads
if "show_map" not in st.session_state:
    st.session_state.show_map = False

# When the button is clicked, remember that the map should be shown
if st.button("Show Route"):
    st.session_state.show_map = True

# Once show_map becomes True, it stays True across reruns
if st.session_state.show_map:

    # Convert place names into coordinates
    origin_coords = get_coordinates(origin)
    destination_coords = get_coordinates(destination)

    if origin_coords is None:
        st.error(f"Could not find '{origin}'")

    elif destination_coords is None:
        st.error(f"Could not find '{destination}'")

    else:
        # Create a map centered on the origin
        m = folium.Map(
            location=origin_coords,
            zoom_start=8
        )

        # Add origin marker
        folium.Marker(
            location=origin_coords,
            popup=origin
        ).add_to(m)

        # Display map
        st_folium(
            m,
            width=700,
            height=500
        )