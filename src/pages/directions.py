# This page will display the individual legs of the trip
# It will show the number of legs, directions from the beginning
# to the end of the leg; and it will show a mini-map of just
# the leg itself.

import streamlit as st

st.title("Directions")

# Check whether a route has been calculated
if "trip_legs" not in st.session_state or not st.session_state.trip_legs:
    st.warning("Create a route in Trip Planner first.")

else:
    st.write(f"{len(st.session_state.trip_legs)} driving legs found.")
    for leg in st.session_state.trip_legs:
        st.subheader(
            f"Leg {leg['leg_number']}"
        )

        st.write(
            f"Distance: {leg['distance_km']:.1f} km"
        )

        st.write(
            f"Driving time: {leg['duration_hours']:.1f} hours"
        )

        st.divider()
