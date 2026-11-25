# Band Tour Planner v1.0

Band Tour Planner is designed to assist touring musicians and crews with long-distance travel planning. The application calculates routes, estimates travel times, schedules recommended breaks, and provides turn-by-turn directions divided into manageable driving sections.

Version 1.0 focuses on routing, maps, directions, and break planning.

Created by Adicus Garton (with a little bitta lotta help by MS Copilot)

---

# Features

- Plan routes between two locations
- Interactive route maps using Folium
- Automatic route calculation using OSRM
- Configurable driving break intervals
- Automatic route segmentation into multiple driving legs
- Turn-by-turn driving directions
- Interactive map for each leg of the journey
- Human-readable stop locations
- Cached route and geocoding requests for improved performance
- Multi-page Streamlit interface

---

# Technologies Used

- Python
- Streamlit
- Folium
- OpenStreetMap
- OSRM (Open Source Routing Machine)
- Nominatim Geocoding
- Geopy
- Requests

---

# Project Structure

```text
Band Tour Planner
│
├── assets/
│   └── hero.jpg
│
├── src/
│   ├── 0_Home.py
│   │
│   └── pages/
│       ├── 1_Trip_Planner.py
│       └── 2_Directions.py
│
├── requirements.txt
├── README.md
└── LICENSE
```

---

# Prerequisites

- Python 3.12.10 or newer (older versions may also work)
- Internet connection (required for route calculation and geocoding)

---

# Required Python Modules

The application uses the following Python packages:

- streamlit
- folium
- streamlit-folium
- geopy
- requests

---

# Installation

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install the project requirements:

```bash
pip install -r requirements.txt
```

---

# Running the Application

From the project root directory:

```bash
streamlit run src/0_Home.py
```

Streamlit will automatically launch the application in your default web browser.

---

# Application Pages

## Home

The Home page introduces the project and provides a brief overview of its purpose and capabilities.

## Trip Planner

The Trip Planner page allows users to:

- Enter a starting location
- Enter a destination
- Choose how long between breaks
- Generate a route & stats
- See an interactive map of the total route

## Directions

The Directions page displays:

- Individual route segments (legs)
- Driving times for each leg
- Distance information
- Interactive leg maps
- Turn-by-turn driving instructions

---

# Performance Optimizations

Band Tour Planner uses Streamlit caching to reduce repeated API calls.

The following functions are cached:

- Route calculation
- Geocoding
- Reverse geocoding

This improves application responsiveness and reduces unnecessary requests to third-party services.

---

# Future Development

Planned enhancements for Version 1.1 and beyond include:

- Multi-day tour planning
- Arrival-time scheduling
- Daily driving limits
- Touring-band scheduling tools
- Route timeline view
- Additional route-management features

---

# License

Released under CC0 1.0 Universal (Public Domain).

You may copy, modify, distribute, and use this project for any purpose without permission.