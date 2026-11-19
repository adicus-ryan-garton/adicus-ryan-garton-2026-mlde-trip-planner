import folium
from streamlit_folium import st_folium

import streamlit as st
from geopy.geocoders import Nominatim

# Page title
st.title("Trip Planner")

# Ask the user for a starting point and destination
origin = st.text_input("Starting location")
destination = st.text_input("Destination")

# Create session variables the first time the app loads

if "show_map" not in st.session_state:
    st.session_state.show_map = False

if "origin_coords" not in st.session_state:
    st.session_state.origin_coords = None

if "destination_coords" not in st.session_state:
    st.session_state.destination_coords = None

if "route_data" not in st.session_state:
    st.session_state.route_data = None

@st.cache_data
def get_coordinates(place):
    print(f"Calling geocoder for {place}")
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

# When the user clicks the button,
# look up and store the coordinates
if st.button("Show Route"):

    st.session_state.origin_coords = get_coordinates(origin)
    st.session_state.destination_coords = get_coordinates(destination)

    st.session_state.show_map = True


# If a route has been requested, display the map
if st.session_state.show_map:

    origin_coords = st.session_state.origin_coords
    destination_coords = st.session_state.destination_coords

    if origin_coords is None:
        st.error(f"Could not find '{origin}'")

    elif destination_coords is None:
        st.error(f"Could not find '{destination}'")

    else:

        # Create map
        m = folium.Map()

        # Start marker
        folium.Marker(
            location=origin_coords,
            popup=f"Start: {origin}",
            tooltip="Start",
            icon=folium.Icon(color="green")
        ).add_to(m)

        # Destination marker
        folium.Marker(
            location=destination_coords,
            popup=f"Destination: {destination}",
            tooltip="Destination",
            icon=folium.Icon(color="red")
        ).add_to(m)

        # Draw route line
        folium.PolyLine(
            locations=[origin_coords, destination_coords],
            color="blue",
            weight=5,
            opacity=0.8
        ).add_to(m)

        # Zoom so both markers are visible
        m.fit_bounds([
            origin_coords,
            destination_coords
        ])

        # Display map
        st_folium(
            m,
            width=700,
            height=500
        )


@st.cache_data
def get_route(origin_coords, destination_coords):
    """
    Ask OSRM for a road route between two locations.

    Returns route geometry and navigation data.
    """

    pass