# This is the trip planner page. This will take your starting and ending locations and produce
# the overall trip details for you. The DIRECTIONS page will take information from this page and
# generate the directions for teh user.

# Developer settings
DEBUG_MODE = False

# más importante
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

# Maximum cruising speed of the vehicle
vehicle_speed = st.number_input(
    "Planned cruising speed (km/h)",
    min_value=30,
    max_value=140,
    value=120
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

if "trip_legs" not in st.session_state:
    st.session_state.trip_legs = []

if "break_interval" not in st.session_state:
    st.session_state.break_interval = 2

if "vehicle_speed" not in st.session_state:
    st.session_state.vehicle_speed = 120


# functions

@st.cache_data(show_spinner=False)
def get_coordinates(place):
    # timeout=10 gives the server more time to respond
    geolocator = Nominatim(user_agent="trip_planner",timeout=10)
    location = geolocator.geocode(place)
    if location:
        return (location.latitude, location.longitude)
    return None


@st.cache_data(show_spinner=False)
def get_place_name(coords):
    """
    Convert coordinates into a human-readable place name.
    """
    geolocator = Nominatim(user_agent="trip_planner",timeout=10)
    location = geolocator.reverse(
        f"{coords[0]}, {coords[1]}",
        language="en"
    )
    if not location:
        return "Unknown location"
    address = location.raw.get("address", {})
    return (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("municipality")
        or "Unknown location"
    )


@st.cache_data(show_spinner=False)
def get_route(origin_coords, destination_coords):
    """
    Ask OSRM for a road route between two locations.
    Returns the JSON response from OSRM.
    Cached so the same route isn't repeatedly requested.
    """
    start_lon = origin_coords[1]
    start_lat = origin_coords[0]
    end_lon = destination_coords[1]
    end_lat = destination_coords[0]

    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{start_lon},{start_lat};{end_lon},{end_lat}"
        f"?overview=full"
        f"&geometries=geojson"
        f"&steps=true"
    )

    response = requests.get(url)
    return response.json()


# When the user clicks the button,
# look up and store the coordinates
if st.button("Show Route"):

    st.session_state.origin_coords = get_coordinates(origin)
    st.session_state.break_interval = break_interval
    st.session_state.vehicle_speed = vehicle_speed
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
    # Route display section
    else:
        # Request a road route from OSRM
        route_data = get_route(origin_coords,destination_coords)

        # Store route data so other pages can use it
        st.session_state.route_data = route_data

        if route_data["code"] != "Ok":
            st.error("Unable to calculate route.")

        # Extract the first route returned by OSRM
        route = route_data["routes"][0]

        steps = route["legs"][0]["steps"]

        # Route statistics
        distance_km = route["distance"] / 1000
        duration_hours = (
                distance_km
                /
                st.session_state.vehicle_speed
        )
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

        # Calculate break points
        break_markers = []

        # Store information about each leg
        trip_legs = []
        steps = route["legs"][0]["steps"]

        break_interval_seconds = (
                st.session_state.break_interval * 3600
        )

        next_break_time = break_interval_seconds

        elapsed_time = 0

        for step in steps:

            step_start_time = elapsed_time

            step_distance_km = (
                    step["distance"] / 1000
            )

            step_duration_seconds = (
                                            step_distance_km
                                            /
                                            st.session_state.vehicle_speed
                                    ) * 3600

            step_end_time = (
                    elapsed_time + step_duration_seconds
            )

            if DEBUG_MODE:
                st.write(
                    f"elapsed={elapsed_time:.0f}, "
                    f"next_break={next_break_time:.0f}, "
                    f"step_end={step_end_time:.0f}"
                )

            while step_end_time >= next_break_time:
                # How far through this step
                # the breakpoint occurs
                fraction = (
                        (next_break_time - step_start_time)
                        /
                        step["duration"]
                )

                geometry_points = (
                    step["geometry"]["coordinates"]
                )

                point_index = int(
                    fraction *
                    (len(geometry_points) - 1)
                )

                point = geometry_points[
                    point_index
                ]

                # Convert from
                # [longitude, latitude]
                # to
                # [latitude, longitude]
                break_markers.append([
                    point[1],
                    point[0]
                ])

                next_break_time += (
                    break_interval_seconds
                )

            elapsed_time = step_end_time

        # Break markers have now been created
        st.write(f"Break markers: {len(break_markers)}")



        stopping_points = [
        origin_coords,
        *break_markers,
        destination_coords
        ]

        # Create individual legs between stopping points
        for index in range(len(stopping_points) - 1):
            leg_start = stopping_points[index]
            leg_end = stopping_points[index + 1]
            leg_route = get_route(leg_start,leg_end)

            route = leg_route["routes"][0]
            start_name = get_place_name(leg_start)
            end_name = get_place_name(leg_end)
            trip_legs.append({
                "leg_number": index + 1,
                "start": leg_start,
                "end": leg_end,
                "start_name": start_name,
                "end_name": end_name,
                "break_interval": st.session_state.break_interval,
                "distance_km": route["distance"] / 1000,
                "duration_hours":
(
    route["distance"] / 1000
)
/
st.session_state.vehicle_speed,

                "route_data": leg_route
            })

        # Save legs for use on other pages
        st.session_state.trip_legs = trip_legs


        # Create map
        m = folium.Map()

        # Start marker
        folium.Marker(
            location=origin_coords,
            popup=f"Start: {origin}",
            tooltip="Start",
            icon=folium.Icon(
                color="green",
                icon="play"
            )
        ).add_to(m)

        # Destination marker
        folium.Marker(
            location=destination_coords,
            popup=f"Destination: {destination}",
            tooltip="Destination",
            icon=folium.Icon(
                color="red",
                icon="flag"
            )
        ).add_to(m)

        # Add break markers, and place-name them
        for index, break_point in enumerate(
                break_markers,
                start=1
        ):
            folium.Marker(
                location=break_point,
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




