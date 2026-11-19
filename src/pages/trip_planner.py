# all dem imports

import folium
from streamlit_folium import st_folium

import streamlit as st
from geopy.geocoders import Nominatim

import requests

import math


# Page title
st.title("Trip Planner")

# Ask the user for a starting point and destination
origin = st.text_input("Starting location")
destination = st.text_input("Destination")

# How long the user wants to drive between breaks
break_interval = st.number_input(
    "Driving time between breaks (hours)",
    min_value=1,
    max_value=8,
    value=2
)

# Create session variables the first time the app loads

if "show_map" not in st.session_state:
    st.session_state.show_map = False

if "origin_coords" not in st.session_state:
    st.session_state.origin_coords = None

if "destination_coords" not in st.session_state:
    st.session_state.destination_coords = None

if "route_data" not in st.session_state:
    st.session_state.route_data = None

if "break_interval" not in st.session_state:
    st.session_state.break_interval = 2


# functions

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

@st.cache_data
def get_route(origin_coords, destination_coords):
    """
    Ask OSRM for a road route between two locations.

    Returns the JSON response from OSRM.

    Cached so the same route isn't repeatedly requested.
    """

    print("Requesting route from OSRM")

    start_lon = origin_coords[1]
    start_lat = origin_coords[0]

    end_lon = destination_coords[1]
    end_lat = destination_coords[0]

    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{start_lon},{start_lat};{end_lon},{end_lat}"
        f"?overview=full&geometries=geojson"
    )

    response = requests.get(url)

    return response.json()

# Create the session variable the first time the page loads
if "show_map" not in st.session_state:
    st.session_state.show_map = False

# When the user clicks the button,
# look up and store the coordinates
if st.button("Show Route"):

    st.session_state.origin_coords = get_coordinates(origin)
    st.session_state.break_interval = break_interval
    st.session_state.destination_coords = get_coordinates(destination)

    # Clear any previous route data.
    # We'll recalculate it when the map is displayed.
    st.session_state.route_data = None

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

        # Request a road route from OSRM
        route_data = get_route(
            origin_coords,
            destination_coords
        )

        # Store route data so other pages can use it
        st.session_state.route_data = route_data

        st.write("OSRM status:", route_data["code"])

        # Extract the first route returned by OSRM
        route = route_data["routes"][0]

        # Route statistics
        distance_km = route["distance"] / 1000
        duration_hours = route["duration"] / 3600
        estimated_legs = math.ceil(
            duration_hours / st.session_state.break_interval
        )
        st.write(f"Distance: {distance_km:.1f} km")
        st.write(f"Driving time: {duration_hours:.1f} hours")
        st.write(
            f"Break every {st.session_state.break_interval} hour(s)"
        )
        st.write(
            f"Estimated driving legs: {estimated_legs}"
        )

        # Extract the route geometry
        geometry = route["geometry"]

        # OSRM returns [longitude, latitude]
        # Folium expects [latitude, longitude]

        road_coordinates = []

        for point in geometry["coordinates"]:
            longitude = point[0]
            latitude = point[1]

            road_coordinates.append(
                [latitude, longitude]
            )

        # Calculate where breaks should occur along the route
        break_markers = []

        # Store information about each leg
        trip_legs = []

        for leg_number in range(1, estimated_legs):
            # Calculate the percentage of the route completed
            route_fraction = leg_number / estimated_legs
            # Find the matching coordinate in the route
            coordinate_index = int(
                route_fraction * len(road_coordinates)
            )
            break_markers.append(
                road_coordinates[coordinate_index]
            )

        # Build a complete list of stopping points
        stopping_points = [
            origin_coords,
            *break_markers,
            destination_coords
        ]

        # Create individual legs between stopping points
        for index in range(len(stopping_points) - 1):
            trip_legs.append({
                "leg_number": index + 1,
                "start": stopping_points[index],
                "end": stopping_points[index + 1]
            })

        # verify trip legs
        st.write("Trip legs")
        for leg in trip_legs:
            st.write(
                f"Leg {leg['leg_number']}: "
                f"{leg['start']} -> {leg['end']}"
            )

        # For debugging
        st.write(f"Route contains {len(geometry['coordinates'])} points")

        # Display the top-level keys returned by OSRM
        st.write(route_data.keys())

        # Display the response status for testing
        st.write("OSRM status:", route_data["code"])


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

        # Add break markers
        for index, break_point in enumerate(
            break_markers,
            start=1
        ):

            folium.Marker(
                location=break_point,
                popup=f"Break {index}",
                tooltip=f"Break {index}",
                icon=folium.Icon(color="orange")
            ).add_to(m)

        # Draw route line
        folium.PolyLine(
            locations=road_coordinates,
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




