# This page will display the individual legs of the trip
# It will show the number of legs, directions from the beginning
# to the end of the leg; and it will show a mini-map of just
# the leg itself.

# Developer settings
DEBUG_MODE = True

import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("Directions")

# Check whether a route has been calculated
if "trip_legs" not in st.session_state or not st.session_state.trip_legs:
    st.warning("Create a route in Trip Planner first.")

else:
    st.write(f"{len(st.session_state.trip_legs)} driving legs found.")
    total_time = 0
    try:
        for leg in st.session_state.trip_legs:
            st.subheader(f"Leg {leg['leg_number']}")
            st.caption(f"{leg['start_name']} → {leg['end_name']}")


            # Extract route geometry for this leg
            route = leg["route_data"]["routes"][0]
            geometry = route["geometry"]

            road_coordinates = []

            for point in geometry["coordinates"]:
                longitude = point[0]
                latitude = point[1]
                road_coordinates.append(
                    [latitude, longitude]
                )

            leg_map = folium.Map()

            folium.PolyLine(
                locations=road_coordinates,
                color="blue",
                weight=5
            ).add_to(leg_map)

            # Start marker

            folium.Marker(
                location=road_coordinates[0],
                popup="Start",
                icon=folium.Icon(color="orange")
            ).add_to(leg_map)

            # End marker

            folium.Marker(
                location=road_coordinates[-1],
                popup="End",
                icon=folium.Icon(color="orange")
            ).add_to(leg_map)

            leg_map.fit_bounds(
                road_coordinates,
                padding=(30, 30)
            )

            st_folium(
                leg_map,
                width=700,
                height=300,
                key=f"leg_map_{leg['leg_number']}"
            )

            st.write(
                f"Distance: {leg['distance_km']:.1f} km"
            )

            st.write(
                f"Driving time: {leg['duration_hours']:.1f} hours"
            )
            total_time += leg["duration_hours"]
            st.write("Directions:")

            steps = (
                leg["route_data"]
                ["routes"][0]
                ["legs"][0]
                ["steps"]
            )

            for step in steps:
                maneuver_type = step["maneuver"]["type"]

                road_name = step["name"]

                distance_km = step["distance"] / 1000

                st.write(
                    f"• {maneuver_type} on "
                    f"{road_name} "
                    f"({distance_km:.1f} km)"
                )
            st.divider()

    except Exception as error:

        if DEBUG_MODE:
            st.exception(error)
        else:
            st.error(
                "Sorry, directions could not be displayed."
            )
st.write(
    f"Total of all legs: {total_time:.1f} hours"
)
