# This page will display the individual legs of the trip
# It will show the number of legs, directions from the beginning
# to the end of the leg; and it will show a mini-map of just
# the leg itself.

# Developer settings
DEBUG_MODE = True

import streamlit as st
import folium
from streamlit_folium import st_folium

# let's make the instructions human-readable directions instead
MANEUVER_TEXT = {
    "depart": "Start on",
    "turn": "Turn onto",
    "continue": "Continue on",
    "new name": "Continue onto",
    "roundabout": "Enter roundabout via",
    "merge": "Merge onto",
    "fork": "Take fork onto",
    "arrive": "Arrive at",
    "end of road": "At end of road, continue onto",
    "notification": "Continue on",
    "off ramp": "Take exit onto",
    "on ramp": "Join",
    "exit roundabout": "Exit roundabout onto"
}

st.title("Directions")

# Check whether a route has been calculated
if "trip_legs" not in st.session_state or not st.session_state.trip_legs:
    st.warning("One does not simply walk into Mordor. You'll need to create a route in Trip Planner first.")

else:
    st.write(f"{len(st.session_state.trip_legs)} driving legs found.")

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

            folium.Marker(
                location=road_coordinates[0],
                popup="Start",
                icon=folium.Icon(
                    color="green",
                    icon="play"
                )
            ).add_to(leg_map)

            folium.Marker(
                location=road_coordinates[-1],
                popup="End",
                icon=folium.Icon(
                    color="red",
                    icon="flag"
                )
            ).add_to(leg_map)

            leg_map.fit_bounds(road_coordinates,padding=(30, 30))

            st_folium(
                leg_map,
                width=700,
                height=300,
                key=f"leg_map_{leg['leg_number']}"
            )

            st.write(f"Distance: {leg['distance_km']:.1f} km")

            st.write(f"Driving time: {leg['duration_hours']:.1f} hours")

            # create directions and hide them under an expander
            with st.expander("Turn-by-turn Directions"):

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

                    # Ignore tiny instructions
                    if distance_km < 0.5:
                        continue

                    instruction = MANEUVER_TEXT.get(
                        maneuver_type,
                        maneuver_type.replace("_", " ").title()
                    )

                    if road_name:
                        text = (
                            f"• {instruction} {road_name} "
                            f"({distance_km:.1f} km)"
                        )
                    else:
                        text = (
                            f"• {instruction} "
                            f"({distance_km:.1f} km)"
                        )

                    st.markdown(
                        f"> {text}"
                    )

            st.divider()
            if leg["leg_number"] == len(st.session_state.trip_legs):

                st.success(f"Final destination reached: {leg['end_name']}")

            else:

                st.info(f"Break stop: {leg['end_name']}")

    except Exception as error:

        if DEBUG_MODE:
            st.exception(error)
        else:
            st.error("Sorry, directions could not be displayed.")

st.divider()

st.caption("Trip Planner 1.0 · Created by Adicus Garton")
